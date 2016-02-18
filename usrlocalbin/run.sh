#!/bin/bash

# Run ansible, but output to stderr
>&2 ansible-playbook -i /ansible/inventory /ansible/$1

# Write resource output to stdout
cat /tmp/resourceOutput.json
