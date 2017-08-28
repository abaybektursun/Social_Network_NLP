from langdetect import detect 

import urllib.request
import requests
import time
import json
import sys
import os

FILE_NAME     = 'Hewlett-Packard-Enterprise_reviews.json'
REQ_ATTEMPTS  = 5
TIMEOUT       = 2

def request_handler(url):
    global REQ_ATTEMPTS; global TIMEOUT;
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
    return None

def translate(text):
    language = detect(text) 
    if language == 'en': 
        return text
    print("@@translated!@@")
    req = "https://translate.yandex.net/api/v1.5/tr.json/translate?" + \
          "key={API_key}"     + \
          "&text=\"{text}\""  + \
          "&lang={direction}"
    req = req.format(API_key=sys.argv[1], text=text, direction=language+'-en')
    translated = request_handler(req)
    return str(translated or '')

with open(FILE_NAME) as indeed_file:
    json_data = json.load(indeed_file)
    translated = []
    for a_review in json_data:
        if a_review['pros']: 
            print(translate(a_review['pros']))
        #if a_review['cons']:
        #if a_review['review_text']:
