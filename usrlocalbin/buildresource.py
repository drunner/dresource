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

# -------------------------------------------------------------
# Arguments
# -------------------------------------------------------------
if len(sys.argv) != 2 or os.environ.get('USERNAME') == None or os.environ.get('AWS_ACCESS_KEY_ID') == None or os.environ.get('AWS_SECRET_ACCESS_KEY') == None:
   print "buildresource.py <CONFIG FILENAME>"
   print "Expects environment variables USERNAME, AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY\n"
   sys.exit()
   
username = os.environ.get('USERNAME')
configFilename = sys.argv[1]

if username == 'PRODUCTION':
   username = ''
else:
   username += '-'
   
# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------
with open(configFilename) as config_file:    
    config = json.load(config_file)
prefix = username + config['projectname'] + '-'

# -------------------------------------------------------------
# Data structure
# -------------------------------------------------------------
resources = {}
resources['s3'] = {}
resources['dynamodb'] = {}

regions = {}

# -------------------------------------------------------------
# Build resource dictionary
# -------------------------------------------------------------

# Build dictionary of required S3 buckets
if 's3' in config:
   for bucketName in config['s3']:
      # Generate full name
      longName = prefix + bucketName
      # Set dictionary values
      resources['s3'][longName] = config['s3'][bucketName]
      resources['s3'][longName]['state'] = 'present'
      # Set default region
      if not 'region' in resources['s3'][longName]:
         resources['s3'][longName]['region'] = 'us-east-1'
      # Record all used regions
      regions[resources['s3'][longName]['region']] = True

# Build dictionary of required DynamoDB tables
if 'dynamodb' in config:
   for tableName in config['dynamodb']:
      # Generate full name
      longName = prefix + tableName
      # Set dictionary values
      resources['dynamodb'][longName] = config['dynamodb'][tableName]
      resources['dynamodb'][longName]['state'] = 'present'
      # Set default region
      if not 'region' in resources['dynamodb'][longName]:
         resources['dynamodb'][longName]['region'] = 'us-east-1'
      # Record all used regions
      regions[resources['dynamodb'][longName]['region']] = True

# -------------------------------------------------------------
# Scan S3
# -------------------------------------------------------------

# Use list of existing buckets to work out what to keep, what to delete
s3Conn = S3Connection(os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY'])
existingBuckets = s3Conn.get_all_buckets()
for bucket in existingBuckets:
   if re.match(prefix, bucket.name):
      if (not bucket.name in resources['s3']):
         resources['s3'][bucket.name] = { 'state' : 'absent' }

# -------------------------------------------------------------
# Scan DynamoDB
# -------------------------------------------------------------

# Use list of existing tables in the regions we care about to work out what to keep, what to delete
for region in regions:
   dyConn = boto.dynamodb2.connect_to_region(
           region,
           aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID'],
           aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY'])
   existingTables = dyConn.list_tables()
   for table in existingTables["TableNames"]:
      if re.match(prefix, table):
         if (not table in resources['dynamodb']):
            resources['dynamodb'][table] = { 'state' : 'absent' }

# -------------------------------------------------------------
# Print out lists
# -------------------------------------------------------------
print json.dumps(resources)
