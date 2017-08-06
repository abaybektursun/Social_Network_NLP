from datetime import datetime, date, time

import urllib.request
import configparser
import logging
import json
import time
import csv
import os.path

SOURCE_PATH = os.path.dirname(os.path.abspath(__file__))
LOG_FILE_NAME = 'fb_scrapper_{}.log'.format(datetime.now().strftime("%Y-%m-%d_%H%M%S"))
REQ_ATTEMPTS = 0
TIMEOUT = 0

# Right working directory
os.chdir(SOURCE_PATH)

# Set up logs
logging.basicConfig(format='%(levelname)s\t%(asctime)s\t%(message)s', filename=LOG_FILE_NAME, datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
logging.info('Application has started')

# Get FB access token
fb_configs = configparser.ConfigParser()
fb_configs.read('key.fbtoken')
token = '{}|{}'.format(fb_configs['app']['id'], fb_configs['app']['secret'])

# Configs
configs = configparser.ConfigParser()
configs.read('config.ini')
REQ_ATTEMPTS = int(configs['default']['REQ_ATTEMPTS'])
TIMEOUT = int(configs['default']['TIMEOUT'])

def request_handler(url):
    global REQ_ATTEMPTS; global TIMEOUT
    req = urllib.request.Request(url); err = ''
    for i in range(REQ_ATTEMPTS):
        try: 
            response = urllib.request.urlopen(req, timeout=TIMEOUT)
            if response.getcode() == 200:
                return response.read()
        except Exception as e:
            time.sleep(2)
            err = str(e)
    logging.error("{}:{}".format(url,err))
    return None

# URL Setup
GRAPH_API = 'https://graph.facebook.com/v2.4'

# DEBUG
print(request_handler(GRAPH_API))
print(request_handler('http://google.com') )
print(request_handler('http://aaaq.com') )
