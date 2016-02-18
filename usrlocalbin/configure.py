#!/usr/bin/python

# -------------------------------------------------------------
# Imports
# -------------------------------------------------------------
import sys
import json
import os.path

# -------------------------------------------------------------
# Arguments
# -------------------------------------------------------------
if len(sys.argv) != 5 or (sys.argv[1] != 'aws' and sys.argv[1] != 'mysql'):
   print "configure.py aws <USERNAME> <AWS_ACCESS_KEY> <AWS_SECRET_KEY>"
   print "   or"
   print "configure.py mysql <HOST> <USERNAME> <PASSWORD>"
   sys.exit()

configFilename = '/config/config.json'

# -------------------------------------------------------------
# Load configuration
# -------------------------------------------------------------
config = {}
if os.path.isfile(configFilename):
   with open(configFilename) as config_file:    
      config = json.load(config_file)

# -------------------------------------------------------------
# Update configuration
# -------------------------------------------------------------
if sys.argv[1] == 'aws':
   config['aws'] = {}
   config['aws']['username'] = sys.argv[2]
   config['aws']['aws_access_key'] = sys.argv[3]
   config['aws']['aws_secret_key'] = sys.argv[4]
   
elif sys.argv[1] == 'mysql':
   config['mysql'] = {}
   config['mysql']['host'] = sys.argv[2]
   config['mysql']['user'] = sys.argv[3]
   config['mysql']['password'] = sys.argv[4]

# -------------------------------------------------------------
# Save configuration
# -------------------------------------------------------------
with open(configFilename, 'w') as outfile:
    json.dump(config, outfile)
