from datetime import datetime, date, time

import urllib.request
import configparser
import logging
import json
import time
import sys
import csv
import os.path

SOURCE_PATH   = os.path.dirname(os.path.abspath(__file__))
LOG_FILE_NAME = 'fb_scrapper_{}.log'.format(datetime.now().strftime("%Y-%m-%d_%H%M%S"))
REQ_ATTEMPTS  = 0
TIMEOUT       = 0
LOGS_FOLDER   = 'logs/'
DATA_FOLDER   = 'data/'
EXPORT_CSV    = False
EXPORT_JSON   = False

# Configs
configs = configparser.ConfigParser()
configs.read('config.ini')
page = configs['default']['page_id']
REQ_ATTEMPTS = int(configs['default']['REQ_ATTEMPTS'])
TIMEOUT      = int(configs['default']['TIMEOUT'])
EXPORT_CSV   = configs['default'].getboolean('EXPORT_CSV' )
EXPORT_JSON  = configs['default'].getboolean('EXPORT_JSON')

if len(sys.argv) >= 2:
    page = sys.argv[1]
# Second arguemnt is the topic (class)
if len(sys.argv) == 3:
    DATA_FOLDER += str(sys.argv[2]) + '/'
    LOGS_FOLDER += str(sys.argv[2]) + '/'

# Right working directory
os.chdir(SOURCE_PATH)

# Set up logs folder
if not os.path.exists(LOGS_FOLDER):
    os.makedirs(LOGS_FOLDER)
# Setup data folder
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Get FB access token
fb_configs = configparser.ConfigParser()
fb_configs.read('key.fbtoken')
token = '{}|{}'.format(fb_configs['app']['id'], fb_configs['app']['secret'])



logging.basicConfig(format='%(levelname)s\t%(asctime)s\t%(message)s', filename='{}/{}_{}'.format(LOGS_FOLDER,page,LOG_FILE_NAME), datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
logging.info('Application has started')
logging.info('Reqeust Attempts:{}, Timeout (secs): {}, Export CSV?: {}, Export JSON?: {}'.format(REQ_ATTEMPTS, TIMEOUT, EXPORT_CSV, EXPORT_JSON))


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


def traverse_posts(page_id, get_reactions=False):
    # Using as a closure *******************************************************************************************************************************
    def a_post_process():
        a_post['comments']        = []
        a_post['reactions']       = []
        a_post['reactions_count'] = {}
                                                                                                                                                         
        #------- Comments ------------------------------------------------------------------------------------------------------------------------------
        req_type = 'comments'
        comments_url = '{root}/{post_id}/{req}/?access_token={token}'.format(root=GRAPH_API,post_id=a_post['id'],req=req_type, token=token)
        while True:
            comments            = request_handler(comments_url)
            json_comment_data   = json.loads(comments)
            a_post['comments'] += json_comment_data['data']


            try:
                comments_url = json_comment_data['paging']['next']
            except KeyError:
                logging.info('Post: {},  Nuber of comments: {}'.format(a_post['id'], len(a_post['comments'])))
                break

        # Write comments to csv file
        if EXPORT_CSV:
            for a_comment in a_post['comments']:
                csv_comments_writer.writerow([
                    a_post['id'],
                    a_comment['id'],
                    a_comment['created_time'],
                    a_comment['from'].get('name',''),
                    a_comment['from']['id'],
                    a_comment['message']
                ])
        #-----------------------------------------------------------------------------------------------------------------------------------------------
        
        #------- Reactions -----------------------------------------------------------------------------------------------------------------------------
        if get_reactions:
            req_type = 'reactions'
            reactions_url = '{root}/{post_id}/{req}/?access_token={token}'.format(root=GRAPH_API,post_id=a_post['id'],req=req_type,token=token)
            while True:
                reactions = request_handler(reactions_url)
                json_reactions_data = json.loads(reactions)
                a_post['reactions'] += json_reactions_data['data']
                                                                                                                                                         
                try:
                    reactions_url = json_reactions_data['paging']['next']
                except KeyError:
                    logging.info('Post: {},  Nuber of reactions: {}'.format(a_post['id'], len(a_post['reactions'])))
                    break
        #-----------------------------------------------------------------------------------------------------------------------------------------------
                                                                                                                                                         
        #------- Reactions Count -----------------------------------------------------------------------------------------------------------------------
        reactions_count_url = '{root}/{post_id}/?fields=reactions.type(LIKE).limit(0).summary(total_count).as(reactions_like),'        \
                                                     + 'reactions.type(LOVE).limit(0).summary(total_count).as(reactions_love),'        \
                                                     + 'reactions.type(WOW).limit(0).summary(total_count).as(reactions_wow),'          \
                                                     + 'reactions.type(HAHA).limit(0).summary(total_count).as(reactions_haha),'        \
                                                     + 'reactions.type(SAD).limit(0).summary(total_count).as(reactions_sad),'          \
                                                     + 'reactions.type(ANGRY).limit(0).summary(total_count).as(reactions_angry),'      \
                                                     + 'reactions.type(THANKFUL).limit(0).summary(total_count).as(reactions_thankful)' \
                                                     + '&access_token={token}'
        reactions_count_url       = reactions_count_url.format(root=GRAPH_API,post_id=a_post['id'],token=token)
        reactions_count           = request_handler(reactions_count_url)
        json_reactions_count_data = json.loads(reactions_count)
        a_post['reactions_count'] = json_reactions_count_data.copy()
        #-----------------------------------------------------------------------------------------------------------------------------------------------
        
        # Write a record to json file
        if EXPORT_JSON: json.dump(a_post, json_file, indent=4) 
        
        # Write a record to CSV file
        if EXPORT_CSV: csv_writer.writerow([  
            a_post['id'],
            a_post.get('from','')['id'],
            a_post.get('from','')['name'],
            a_post.get('message',''),
            a_post.get('link', ''),
            a_post.get('tags',''),
            a_post.get('object_attachment',''),
            a_post['created_time'],
            a_post.get('description',''),
            a_post['reactions_count']['reactions_like'    ]['summary']['total_count'],
            a_post['reactions_count']['reactions_love'    ]['summary']['total_count'],
            a_post['reactions_count']['reactions_wow'     ]['summary']['total_count'],
            a_post['reactions_count']['reactions_haha'    ]['summary']['total_count'],
            a_post['reactions_count']['reactions_sad'     ]['summary']['total_count'],
            a_post['reactions_count']['reactions_angry'   ]['summary']['total_count'],
            a_post['reactions_count']['reactions_thankful']['summary']['total_count']  
        ])
        
    # Closure End **************************************************************************************************************************************
    
    global token
    req_type = 'feed'
    fields='from,message,link,tags,object_attachment,created_time,description'
    url = '{root}/{page}/{req}/?fields={fields}&access_token={token}'.format(root=GRAPH_API,page=page,req=req_type,fields=fields,token=token) 
    num_posts = 0
    with open(DATA_FOLDER+page+'_page.json', 'w') as json_file, open(DATA_FOLDER+page+'_page.csv', 'w') as csv_file, open(DATA_FOLDER+page+'_page_comments.csv', 'w') as csv_comments_file:    
        csv_writer = csv.writer(csv_file)
        csv_comments_writer = csv.writer(csv_comments_file)
        
        json_file.write('[')

        # Process 1st post separately to avoid branching
        data = request_handler(url)
        if data:
            json_feed_data = json.loads(data)
            a_post = json_feed_data['data'][0]
            a_post_process()
            try:
                url = json_feed_data['paging']['next']
            except KeyError:
                return
        else: return 
        # All the posts starting from the second one
        while True:
            data = request_handler(url)
            if not data: 
                print('Request failed')
                break

            json_feed_data = json.loads(data)
            for a_p in json_feed_data['data'][1:]:
                a_post = a_p.copy()
                json_file.write(',')
                a_post_process()

            num_posts += len(json_feed_data['data'])
            try:
                url = json_feed_data['paging']['next']
            except KeyError:
                logging.info('Scrapped posts: {}'.format(num_posts))
                break
            print("-----------------------------NEXT PAGE----------------------------------------")
        json_file.write(']')

# DEBUG
#print(request_handler(GRAPH_API))
#print(request_handler('http://google.com') )
#print(request_handler('http://aaaq.com') )

# URL Setup
GRAPH_API = 'https://graph.facebook.com/v2.10'

# FB Page: 2D-women-are-the-only-possible-path-to-the-success-of-humanity-as-a-species
#page = '762580480426589'

# FB Page: DXC Technology
#page = 'DXCTechnology'

# FB: page: StealYoWaifu
#page = 'StealYoWaifu'

traverse_posts(page)



















