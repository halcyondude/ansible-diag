#!/bin/bash

set -x
BASE_DIR=$(pwd)/plugins/v2_callback
export ANSIBLE_CALLBACK_PLUGINS=$BASE_DIR/debug_log_json:$BASE_DIR/profile_timeline

#ansible-playbook -vvvv playbooks/one-single-task.yml
ansible-playbook -vvvv playbooks/create-sample-data.yml