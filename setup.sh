#!/bin/bash
# LINUX/MAC only
# Create virtual environment, install requirements and run app
python3 -m venv virtualenv
./virtualenv/bin/pip3 install -r requirements.txt
./virtualenv/bin/python3 main.py
