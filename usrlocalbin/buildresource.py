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
if len(sys.argv) != 4 or os.environ.get('AWS_ACCESS_KEY_ID') == None or os.environ.get('AWS_SECRET_ACCESS_KEY') == None:
   print "buildresource.py <USERNAME> <CONFIG FILENAME> <OUTPUT FILENAME>"
   print "Expects environment variables AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY\n"
   sys.exit()
   
username = sys.argv[1]
configFilename = sys.argv[2]
outputFilename = sys.argv[3]

# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------
with open(configFilename) as config_file:    
    config = json.load(config_file)
projectname = config["projectname"]

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
for bucketName in config['s3']:
   # Generate full name
   longName = username + '-' + projectname + '-' + bucketName
   # Set dictionary values
   resources['s3'][longName] = config['s3'][bucketName]
   resources['s3'][longName]['state'] = 'create'
   # Set default region
   if not 'region' in resources['s3'][longName]:
      resources['s3'][longName]['region'] = 'us-east-1'
   # Record all used regions
   regions[resources['s3'][longName]['region']] = True

# Build dictionary of required DynamoDB tables
for tableName in config['dynamodb']:
   # Generate full name
   longName = username + '-' + projectname + '-' + tableName
   # Set dictionary values
   resources['dynamodb'][longName] = config['dynamodb'][tableName]
   resources['dynamodb'][longName]['state'] = 'create'
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
   if re.match(username + '-' + projectname + '-', bucket.name):
      if (bucket.name in resources['s3']):
         resources['s3'][bucket.name]['state'] = 'update'
      else:
         resources['s3'][bucket.name] = { 'state' : 'delete' }

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
      if re.match(username + '-' + projectname + '-', table):
         if (table in resources['dynamodb']):
            resources['dynamodb'][table]['state'] = 'update'
         else:
            resources['dynamodb'][table] = { 'state' : 'delete' }

# -------------------------------------------------------------
# Print out lists
# -------------------------------------------------------------
with open(outputFilename, 'w') as outfile:
    json.dump(resources, outfile)
