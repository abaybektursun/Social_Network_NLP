from datetime      import datetime, date, time
from html.entities import name2codepoint
from bs4           import BeautifulSoup
from html.parser   import HTMLParser
from unidecode     import unidecode

import urllib.request
import configparser
import os.path
import logging
import codecs
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
COMPANY_NAME  = 'google'

# Right working directory
os.chdir(SOURCE_PATH)

# Set up logs
if not os.path.exists(LOGS_FOLDER):
    os.makedirs(LOGS_FOLDER)

logging.basicConfig(format='%(levelname)s\t%(asctime)s\t%(message)s', filename='{}/{}'.format(LOGS_FOLDER,LOG_FILE_NAME), datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
logging.info('Application has started')


# Configs
configs = configparser.ConfigParser()
configs.read('config.ini')
COMPANY_NAME = configs['default']['COMPANY_NAME']
REQ_ATTEMPTS = int(configs['default']['REQ_ATTEMPTS'])
TIMEOUT      = int(configs['default']['TIMEOUT'])
EXPORT_CSV   = configs['default'].getboolean('EXPORT_CSV' )
EXPORT_JSON  = configs['default'].getboolean('EXPORT_JSON')
logging.info('Company:{}, Reqeust Attempts:{}, Timeout (secs): {}, Export CSV?: {}, Export JSON?: {}'.format(COMPANY_NAME, REQ_ATTEMPTS, TIMEOUT, EXPORT_CSV, EXPORT_JSON))

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


def manual_string(tag):
    str_out = ''; do = True
    if str(tag)[0] == '<': do = False
    for l in str(tag)[1:]:
        if l == '<': do = False
        if do:
            str_out += l
        else:
            if l == '>': do = True
    return str_out

#.......................................................................................................................................................
onetime_use_req = str(request_handler('https://www.indeed.com/cmp/{comp}/reviews?fcountry=ALL&start={page_num}'.format(comp=COMPANY_NAME,page_num='0')))
soup = BeautifulSoup(onetime_use_req, 'html.parser')
total_num_reviews = 0
try:
    total_num_reviews = int(re.sub("\D", "", soup.find(attrs={"class":"cmp-filter-result"}).string))
except Exception as e:
    total_num_reviews = int(re.sub("\D", "", manual_string(soup) ) )
#.......................................................................................................................................................

with open(COMPANY_NAME+'_reviews.json', 'w', encoding='utf-8') as json_file, open(COMPANY_NAME+'_reviews.csv', 'w') as csv_file:  
    json_file.write('[')
    total_reviews_fact = 0
    for page_num in [x for x in range(total_num_reviews) if x % 20 == 0]:
        a_document = str(request_handler('https://www.indeed.com/cmp/{comp}/reviews?fcountry=ALL&start={page_num}'.format(comp=COMPANY_NAME,page_num=page_num)))
        #if not a_document: continue
        soup = BeautifulSoup(a_document, 'html.parser')
        review_containers = soup.find_all(attrs={"class": "cmp-review-container"})
        reviews_list = []
     
        for a_review_container in review_containers:
            if str(a_review_container.parent.get("id")) == 'cmp-review-featured-container': continue
        
            review_id            = a_review_container.find(attrs={"class": "cmp-review"}).get('data-tn-entityid')
            overall_review_score = a_review_container.find(attrs={"itemprop": "ratingValue"}).get('content')
            poster_location      = a_review_container.find(attrs={"class":"cmp-reviewer-job-location"})
            if poster_location:
                poster_location = poster_location.string
            post_date            = a_review_container.find(attrs={"class":"cmp-review-date-created"}).string
            scores_dict = parse_score_table(a_review_container.find(attrs={"class": "cmp-ratings-expanded"}))
            
            review_title = ''; poster_role = ''; status = ''; review_text = u''
           
            pros = a_review_container.find(attrs={"class":"cmp-review-pro-text"})
            cons = a_review_container.find(attrs={"class":"cmp-review-con-text"})
            if pros: pros = pros.string
            if cons: cons = manual_string(cons)
             
            for a_child in a_review_container.find(attrs={"class":"cmp-review-text"}).children:
                review_text += str(a_child.string or ' ')
            
            for a_child in a_review_container.find(attrs={"class":'cmp-reviewer-job-title'}):
                if a_child.name == 'span': continue
                status = a_child.string.replace('–','').replace('(','').replace(')','').strip()

        
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
                "review_title": review_title,
                "poster_status": status,
                "psoter_location":poster_location,
                "post_date": post_date,
                "review_text": review_text,
                "pros": pros,
                "cons": cons
            }
        
            reviews_list.append(a_review)
            #print(a_review)
            #print("--------------------------------------------------------------")
        logging.info('# processed reviews from the page: {}'.format(len(reviews_list)))
        total_reviews_fact += len(reviews_list)
    
        #json_data = json.dumps(reviews_list)
        
        if not page_num == 0: json_file.write(',')
        json.dump(reviews_list[0], json_file, indent=4, ensure_ascii=False) 
        for a_review_dict in reviews_list[1:]:
            json_file.write(',') 
            json.dump(a_review_dict, json_file, indent=4, ensure_ascii=False)
    
    logging.info('# scraped reviews: {}, # reviews according to website: {}'.format(total_reviews_fact,total_num_reviews))
    json_file.write(']')
    
