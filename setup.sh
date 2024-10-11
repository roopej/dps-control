#!/bin/bash

python3 -m venv virtualenv
./virtualenv/bin/pip3 install -r requirements.txt
./virtualenv/bin/python3 dps_control.py
