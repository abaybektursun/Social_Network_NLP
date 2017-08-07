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

def traverse_posts(page_id, get_reactions=False):
    global token
    req_type = 'feed'
    fields='from,message,link,tags,object_attachment,created_time,description'
    url = '{root}/{page}/{req}/?fields={fields}&access_token={token}'.format(root=GRAPH_API,page=page,req=req_type,fields=fields,token=token) 
    #Debug
    #print(url)

    # Debug
    #print (json.dumps(json_feed_data, indent=4, sort_keys=True))
    num_posts = 0
    with open('DXC_tech_page.json', 'w') as outfile:
        outfile.write('[')
        data = request_handler(url)
        if not data:
            print('Request failed')

        json_feed_data = json.loads(data)
        a_post = json_feed_data['data'][0]
        
        #Debug
        print(url)

        json.dump(a_post, outfile, indent=4)
        
        try:
            url = json_feed_data['paging']['next']
        except KeyError:
            return

        while True:
            data = request_handler(url)
            if not data: 
                print('Request failed')
                break
            
            json_feed_data = json.loads(data)
            for a_p in json_feed_data['data'][1:]:
                a_post = a_p.copy()
                a_post['comments']        = []
                a_post['reactions']       = []
                a_post['reactions_count'] = {}
                outfile.write(',')

                #------- Comments ------------------------------------------------------------------------------------------------------------------------------
                req_type = 'comments'
                comments_url = '{root}/{post_id}/{req}/?access_token={token}'.format(root=GRAPH_API,post_id=a_post['id'],req=req_type, token=token)
                while True:
                    comments = request_handler(comments_url)
                    json_comment_data = json.loads(comments)
                    a_post['comments']  += json_comment_data['data'] 
                    
                    try:
                        comments_url = json_comment_data['paging']['next']
                    except KeyError:
                        logging.info('Post: {},  Nuber of comments: {}'.format(a_post['id'], len(a_post['comments'])))
                        break
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
                json.dump(a_post, outfile, indent=4)


            num_posts += len(json_feed_data['data'])
            try:
                url = json_feed_data['paging']['next']
            except KeyError:
                logging.info('Scrapped posts: {}'.format(num_posts))
                break
            print("-----------------------------NEXT PAGE----------------------------------------")
        outfile.write(']')

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



















