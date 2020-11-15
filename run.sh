#!/usr/bin/env bash
python -u manage.py migrate
python -u manage.py fetch &
python -u manage.py sync
