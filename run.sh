#!/usr/bin/env bash
python3 -u manage.py migrate
python3 -u manage.py fetch &
python3 -u manage.py sync
