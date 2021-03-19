#!/bin/bash

python3 -m venv fda-scraper
. fda-scraper/bin/activate
pip install -r requirements.txt
deactivate
