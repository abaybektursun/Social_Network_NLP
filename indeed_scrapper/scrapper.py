from datetime      import datetime, date, time
from html.entities import name2codepoint
from html.parser   import HTMLParser

import urllib.request
import configparser
import os.path
import logging
import json
import time
import csv

SOURCE_PATH   = os.path.dirname(os.path.abspath(__file__))
LOG_FILE_NAME = 'fb_scrapper_{}.log'.format(datetime.now().strftime("%Y-%m-%d_%H%M%S"))
REQ_ATTEMPTS  = 0
TIMEOUT       = 0
LOGS_FOLDER   = 'logs'
EXPORT_CSV    = False
EXPORT_JSON   = False

# Right working directory
os.chdir(SOURCE_PATH)
