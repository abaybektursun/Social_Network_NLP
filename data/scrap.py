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
            resp_code = response.getcode()
            if resp_code == 200:
                return response.read()
        except Exception as e:
            err = str(e)
            time.sleep(2)
    logging.error("{}:{}".format(url,err))
    return None

def traverse_posts(page_id):
    global token
    req_type = 'feed'
    fields='message,link,tags,object_attachment,created_time'
    url = '{root}/{page}/{req}/?fields={fields}&access_token={token}'.format(root=GRAPH_API,page=page,req=req_type,fields=fields,token=token) 
    #Debug
    #print(url)

    # Debug
    #print (json.dumps(json_data, indent=4, sort_keys=True))
    num_posts = 0
    with open('DXC_tech_page.json', 'w') as outfile:
        while True:
            data = request_handler(url)
            if not data: 
                print('Request failed')
                break
            
            json_data = json.loads(data)
            json.dump(json_data['data'], outfile)
            num_posts += len(json_data['data'])
            print('Number of posts: {}'.format(num_posts))
            try:
                url = json_data['paging']['next']
            except KeyError:
                logging.info('Scrapped posts: {}'.format(num_posts))
                break

            print("-----------------------------NEXT PAGE----------------------------------------")
    

# DEBUG
#print(request_handler(GRAPH_API))
#print(request_handler('http://google.com') )
#print(request_handler('http://aaaq.com') )

# URL Setup
GRAPH_API = 'https://graph.facebook.com/v2.10'

# FB Page: 2D-women-are-the-only-possible-path-to-the-success-of-humanity-as-a-species
#page = '762580480426589'

# FB Page: DXC Technology
page = 'DXCTechnology'

traverse_posts(page)



















