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
    language = ''
    try: language = detect(text)
    except: return text
    print("language: "+language)
    if language == 'en' or 'en' in detect_langs(text): 
        return text
    print("@@translated!@@")
    req = "https://translate.yandex.net/api/v1.5/tr.json/translate?" + \
          "key={API_key}"     + \
          "&text=\"{text}\""  + \
          "&lang={direction}"
    try: req = req.format(API_key=sys.argv[1], text=text, direction=language+'-en')
    except: print("You need to provide Yandex API key as a first parameter")
    translated = ''
    req_data = request_handler(req)
    if req_data: translated_json = json.loads(req_data)
    else: return ''
    try: translated = translated_json["text"][0].replace("'", "").replace('"', '')
    except: pass
    return str(translated or '')

translated = []
with open(FILE_NAME) as indeed_file:
    json_data = json.load(indeed_file)
    for a_review in json_data:
        a_review_save = a_review.copy()
        if a_review['pros']: 
            a_review_save['pros'] = translate(a_review['pros'])
            print('-----PROS:\n'+a_review_save['pros'])
        if a_review['cons']:
            a_review_save['cons'] = translate(a_review['cons'])
            print('-----CONS:\m' + a_review_save['cons'])
        if a_review['review_text']:
            a_review_save['review_text'] = translate(a_review['review_text'])
            print('-----REV:\n'+a_review_save['review_text'])
        translated.append(a_review_save)

with open('TRANSLATED_' + FILE_NAME, 'w') as indeed_file:
    json.dump(translated, indeed_file)
