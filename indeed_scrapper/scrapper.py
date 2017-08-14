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
import re

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



#****************************************************************************************************
def parse_score_table(table):
    score_dict = {}
    for a_tr in table.find_all('tr'):
        buffer_score = ['',0] #[type,score]
        for a_td in a_tr.children:     
            if a_td.get('class') == ['cmp-star-cell']:
                # Get the score
                buffer_score[1] = int(float(re.findall(r"[-+]?\d*\.\d+|\d+", a_td.find(attrs={"class": 'cmp-rating-inner rating'}).get('style'))[0])) / 20
            else:
                # Get the score type
                buffer_score[0] = a_td.string.replace(' ', '_').replace('/','_')
        score_dict[buffer_score[0]] = buffer_score[1]
    return score_dict
#****************************************************************************************************

a_document = str(request_handler('https://www.indeed.com/cmp/Dxc-Technology/reviews?fcountry=ALL&start=0'))
soup = BeautifulSoup(a_document, 'html.parser')
review_containers = soup.find_all(attrs={"class": "cmp-review-container"})

for a_review_container in review_containers:
    review_id = a_review_container.find(attrs={"class": "cmp-review"}).get('data-tn-entityid')
    overall_review_score = a_review_container.find(attrs={"itemprop": "ratingValue"}).get('content')
    scores_dict = parse_score_table(a_review_container.find(attrs={"class": "cmp-ratings-expanded"}))
    review_title = ''; poster_role = ''
    for a_span in a_review_container.find(attrs={"class":"cmp-review-title"}).children:
        if a_span.get("itemprop") == "name":
            review_title = a_span.string
        elif a_span.get("itemprop") == "author":
            poster_role = a_span.find('meta').get('content')
    

    a_review = { 
        "review_id": review_id,
        "overall_review_score": overall_review_score,
        "scores": scores_dict,
        "poster_role": poster_role,
        "review_title": review_title
    }
    print(a_review)
    print("--------------------------------------------------------------")

print("reviews: {}".format(len(review_containers)))
