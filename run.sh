#!/bin/bash

. .venv/bin/activate
python monitor.py >> log/log 2>&1 & disown
#python monitor.py
