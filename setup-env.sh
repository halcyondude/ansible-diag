#!/bin/bash

set -x

virtualenv .venv
source .venv/bin/activate
pip install -U -r requirements.txt


