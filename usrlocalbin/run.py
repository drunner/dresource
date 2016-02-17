#!/bin/bash
set -o nounset

if [ ! -e "/config/config.sh" ]; then die "dresource needs to be configured.">&2 ; fi
if [ ! -e "/resources/resources.cfg" ]; then die "dresource requires a resource.cfg file in the configuration folder.">&2 ; fi
source /config/config.sh

ansible-playbook -i /ansible/inventory /ansible/$1
