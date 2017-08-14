from datetime      import datetime, date, time
from html.entities import name2codepoint
from bs4           import BeautifulSoup
from html.parser   import HTMLParser


import urllib.request
import configparser
import os.path
import logging
import json
import time
import csv

SOURCE_PATH   = os.path.dirname(os.path.abspath(__file__))
LOG_FILE_NAME = 'indeed_scrapper_{}.log'.format(datetime.now().strftime("%Y-%m-%d_%H%M%S"))
REQ_ATTEMPTS  = 1
TIMEOUT       = 1
LOGS_FOLDER   = 'logs'
EXPORT_CSV    = False
EXPORT_JSON   = False

# Right working directory
os.chdir(SOURCE_PATH)

# Set up logs
if not os.path.exists(LOGS_FOLDER):
    os.makedirs(LOGS_FOLDER)

logging.basicConfig(format='%(levelname)s\t%(asctime)s\t%(message)s', filename='{}/{}'.format(LOGS_FOLDER,LOG_FILE_NAME), datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
logging.info('Application has started')

class Indeed_HTML_Parser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print("Start tag:", tag)
        for attr in attrs:
            print("     attr:", attr)

    def handle_endtag(self, tag):
        print("End tag  :", tag)

    def handle_data(self, data):
        print("Data     :", data)

    def handle_comment(self, data):
        print("Comment  :", data)

    def handle_entityref(self, name):
        c = chr(name2codepoint[name])
        print("Named ent:", c)

    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
        print("Num ent  :", c)

    def handle_decl(self, data):
        print("Decl     :", data)

def request_handler(url):
    global REQ_ATTEMPTS; global TIMEOUT; global logging
    req = urllib.request.Request(url); err = ''
    for i in range(REQ_ATTEMPTS):
        try:
            response = urllib.request.urlopen(req, timeout=TIMEOUT)
            resp_code = response.getcode()
            if resp_code == 200:
                return response.read()
        except Exception as e:
            err = str(e)
            time.sleep(2)
    logging.error("{}:{}".format(url,err))
    return None

a_document = str(request_handler('https://www.indeed.com/cmp/Dxc-Technology/reviews?fcountry=ALL&start=0'))
parser = Indeed_HTML_Parser()
parser.feed(a_document)

soup = BeautifulSoup(html_doc, 'html.parser')

