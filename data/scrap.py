from datetime import datetime, date, time

import urllib.request
import configparser
import logging
import json
import time
import csv
import os.path

SOURCE_PATH = os.path.dirname(os.path.abspath(__file__))
LOG_FILE_NAME = 'fb_scrapper_{}.log'.format(datetime.now().strftime("%Y-%m-%d_%H%M"))

# Right working directory
os.chdir(SOURCE_PATH)

# Set up logs
logging.basicConfig(filename=LOG_FILE_NAME, datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info('Application has started')

# Get FB access token
configs = configparser.ConfigParser()
configs.read('key.fbtoken')
token = '{}|{}'.format(configs['app']['id'], configs['app']['secret'])


