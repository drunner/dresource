#!/usr/bin/python

# -------------------------------------------------------------
# Imports
# -------------------------------------------------------------
from boto.s3.connection import S3Connection
import boto.dynamodb2
import sys
import re
import json
import os
from os import urandom

# -------------------------------------------------------------
# Arguments
# -------------------------------------------------------------
if len(sys.argv) != 1:
   print "buildResourceList.py"
   sys.exit()

configFilename = '/config/config.json'
resourceConfigFilename = '/resources/resources.cfg'
   
# -------------------------------------------------------------
# Load Configuration
# -------------------------------------------------------------
config = {}
if not os.path.isfile(configFilename):
   print "dresource needs to be configured";
   sys.exit()

with open(configFilename) as config_file:    
    config = json.load(config_file)

username = config['aws']['username']
if username == 'PRODUCTION':
   username = ''
else:
   username += '-'

with open(resourceConfigFilename) as resource_config_file:    
    resourceConfig = json.load(resource_config_file)
prefix = username + resourceConfig['projectname'] + '-'

# -------------------------------------------------------------
# Data structures
# -------------------------------------------------------------
resources = {}
resources['s3'] = {}
resources['dynamodb'] = {}
resources['mysql_schema'] = {}
resources['mysql_user'] = {}

shortResources = {}

regions = {}

# -------------------------------------------------------------
# Build resource dictionary
# -------------------------------------------------------------

# Build dictionary of required S3 buckets
if 's3' in resourceConfig:
   for bucketName in resourceConfig['s3']:
      # Generate full name
      longName = prefix + bucketName
      # Set dictionary values
      resources['s3'][longName] = resourceConfig['s3'][bucketName].copy()
      resources['s3'][longName]['state'] = 'present'
      # Set default region
      if not 'region' in resources['s3'][longName]:
         resources['s3'][longName]['region'] = 'us-east-1'
      
      # Record all used regions
      regions[resources['s3'][longName]['region']] = True
      
      # Record short form of resource for writing out
      if not 's3' in shortResources:
         shortResources['s3'] = {}
      shortResources['s3'][bucketName] = {}
      shortResources['s3'][bucketName]['name'] = longName
      shortResources['s3'][bucketName]['region'] = resources['s3'][longName]['region']

# Build dictionary of required DynamoDB tables
if 'dynamodb' in resourceConfig:
   for tableName in resourceConfig['dynamodb']:
      # Generate full name
      longName = prefix + tableName
      # Set dictionary values
      resources['dynamodb'][longName] = resourceConfig['dynamodb'][tableName].copy()
      resources['dynamodb'][longName]['state'] = 'present'
      # Set default region
      if not 'region' in resources['dynamodb'][longName]:
         resources['dynamodb'][longName]['region'] = 'us-east-1'

      # Record all used regions
      regions[resources['dynamodb'][longName]['region']] = True
      
      # Record short form of resource for writing out
      if not 'dynamodb' in shortResources:
         shortResources['dynamodb'] = {}
      shortResources['dynamodb'][tableName] = {}
      shortResources['dynamodb'][tableName]['name'] = longName
      shortResources['dynamodb'][tableName]['region'] = resources['dynamodb'][longName]['region']

# Build dictionary of required MySQL Schema
if 'mysql' in resourceConfig:
   if not 'mysql' in config:
      die 'dresource is not configured to control mysql'
      
   for schemaName in resourceConfig['mysql']:
      # Generate full name
      longName = prefix + schemaName
      # Set dictionary values
      resources['mysql_schema'][longName] = {}
      resources['mysql_schema'][longName]['login_host'] = config['mysql']['host']
      resources['mysql_schema'][longName]['login_user'] = config['mysql']['user']
      resources['mysql_schema'][longName]['login_password'] = config['mysql']['password']
      resources['mysql_schema'][longName]['state'] = 'present'
      resources['mysql_schema'][longName]['schema_file'] = resourceConfig['mysql'][schemaName]['schema_file']
      
      # Record short form of resource for writing out
      if not 'mysql_schema' in shortResources:
         shortResources['mysql_schema'] = {}
      shortResources['mysql_schema'][schemaName] = {}
      shortResources['mysql_schema'][schemaName]['name'] = longName
      
      # Build dictionary of require MySQL Users
      if 'users' in resourceConfig['mysql'][schemaName]:
         for userName in resourceConfig['mysql'][schemaName]['users']:
            # Generate full name
            longName = prefix + userName
            
            # Generate password
            chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
            password = "".join([chars[ord(c) % len(chars)] for c in urandom(30)])
            
            # Set dictionary values
            resources['mysql_user'][longName] = {}
            resources['mysql_user'][longName]['login_host'] = config['mysql']['host']
            resources['mysql_user'][longName]['login_user'] = config['mysql']['user']
            resources['mysql_user'][longName]['login_password'] = config['mysql']['password']
            resources['mysql_user'][longName]['state'] = 'present'
            resources['mysql_user'][longName]['password'] = password
            resources['mysql_user'][longName]['privileges'] = resourceConfig['mysql'][schemaName]['users'][userName]['privileges']
      
            # Record short form of resource for writing out
            if not 'mysql_user' in shortResources:
               shortResources['mysql_user'] = {}
            shortResources['mysql_user'][schemaName] = {}
            shortResources['mysql_user'][schemaName]['name'] = longName
            shortResources['mysql_user'][schemaName]['password'] = password
      

# -------------------------------------------------------------
# Scan S3
# -------------------------------------------------------------

# Use list of existing buckets to work out what to delete
s3Conn = S3Connection(config['aws']['aws_access_key'], config['aws']['aws_secret_key'])
existingBuckets = s3Conn.get_all_buckets()
for bucket in existingBuckets:
   if re.match(prefix, bucket.name):
      if (not bucket.name in resources['s3']):
         resources['s3'][bucket.name] = { 'state' : 'absent' }

# -------------------------------------------------------------
# Scan DynamoDB
# -------------------------------------------------------------

# Use list of existing tables in the regions we care about to work out what to delete
for region in regions:
   dyConn = boto.dynamodb2.connect_to_region(
           region,
           aws_access_key_id = config['aws']['aws_access_key'],
           aws_secret_access_key = config['aws']['aws_secret_key'])
   existingTables = dyConn.list_tables()
   for table in existingTables["TableNames"]:
      if re.match(prefix, table):
         if (not table in resources['dynamodb']):
            resources['dynamodb'][table] = { 'state' : 'absent' }

# -------------------------------------------------------------
# Write out smaller list for app configuration
# -------------------------------------------------------------
with open('/tmp/resourceOutput.json', 'w') as outfile:
    json.dump(shortResources, outfile, indent=4, separators=(',', ': '))

# -------------------------------------------------------------
# Print out full list for ansible to use
# -------------------------------------------------------------
print json.dumps(resources)
