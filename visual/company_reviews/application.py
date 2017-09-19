#!/usr/local/bin/python3.6

from flask    import render_template, Flask, jsonify, request
from datetime import datetime, date, time

import tensorflow as tf
import numpy      as np

import pymysql.cursors
import configparser
import logging
import pickle
import json
import time
import sys
import os
import re


###########################################################################################################################################################################
LOG_FILE_NAME = 'company_reviews_{}.log'.format(datetime.now().strftime("%Y-%m-%d_%H%M%S"))
LOGS_FOLDER   = 'logs'

# Set up logs
if not os.path.exists(LOGS_FOLDER):
    os.makedirs(LOGS_FOLDER)
logging.basicConfig(format='%(levelname)s\t%(asctime)s\t%(message)s', filename='{}/{}'.format(LOGS_FOLDER,LOG_FILE_NAME), datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
logging.info('Application has started')

sys.path.append('../../indeed_scrapper/')
#from indeed_scrapper import run

# Database
dbconfigs = configparser.ConfigParser()
dbconfigs.read('msql.dbcredentials')
try: connection   = pymysql.connect(
    host     = dbconfigs['default']['HOST'],
    user     = dbconfigs['default']['USER'],
    password = dbconfigs['default']['PASS'],
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
);
except Exception as ex: exit("Failed to connect to database", 2); logging.error(str(ex))
DB_cursor = connection.cursor()

# tSNE
VOCAB_SIZE = 5000
embedding_size = 128
with open('../../word_embeddings/key_reverse_hash_map.pkl','rb') as pickleFile:
    key_reverse_hash_map = pickle.load(pickleFile)

tf.reset_default_graph()

embeddings = tf.get_variable("embeddings",[VOCAB_SIZE, embedding_size])
norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keep_dims=True))
normalized_embeddings = embeddings / norm

saver = tf.train.Saver()

# Use the saver object normally after that.
with tf.Session() as sess:
    embeddings.initializer.run()
    saver.restore(sess, "../../word_embeddings/{}/{}-90000".format(MODEL_FOLDER_NAME, TOPIC) )
    final_embeddings = normalized_embeddings.eval()

tsne = TSNE(perplexity=30, n_components=2, init='pca', n_iter=5000)
n_d_embeddings = tsne.fit_transform(final_embeddings[1:NUM_POINTS+1, :])

# Debug
def plot(embeddings, labels):
    assert embeddings.shape[0] >= len(labels), 'More labels than embeddings'
    pylab.figure(figsize=(15,15))  # in inches
    for i, label in enumerate(labels):
        x, y = embeddings[i,:]
        pylab.scatter(x, y)
        pylab.annotate(label, xy=(x, y), xytext=(5, 2), textcoords='offset points',
                     ha='right', va='bottom')
    pylab.show()

words = [key_reverse_hash_map[i] for i in range(1, NUM_POINTS+1)]

###########################################################################################################################################################################



#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# TODO!
def parse_location(raw_location):
    states = [("Alabama","AL"),
              ("Alaska","AK"),
              ("Arizona","AZ"),
              ("Arkansas","AR"),
              ("California","CA"),
              ("Colorado","CO"),
              ("Connecticut","CT"),
              ("Delaware","DE"),
              ("District of Columbia","DC"),
              ("Florida","FL"),
              ("Georgia","GA"),
              ("Hawaii","HI"),
              ("Idaho","ID"),
              ("Illinois","IL"),
              ("Indiana","IN"),
              ("Iowa","IA"),
              ("Kansas","KS"),
              ("Kentucky","KY"),
              ("Louisiana","LA"),
              ("Maine","ME"),
              ("Montana","MT"),
              ("Nebraska","NE"),
              ("Nevada","NV"),
              ("New Hampshire","NH"),
              ("New Jersey","NJ"),
              ("New Mexico","NM"),
              ("New York","NY"),
              ("North Carolina","NC"),
              ("North Dakota","ND"),
              ("Ohio","OH"),
              ("Oklahoma","OK"),
              ("Oregon","OR"),
              ("Maryland","MD"),
              ("Massachusetts","MA"),
              ("Michigan","MI"),
              ("Minnesota","MN"),
              ("Mississippi","MS"),
              ("Missouri","MO"),
              ("Pennsylvania","PA"),
              ("Rhode Island","RI"),
              ("South Carolina","SC"),
              ("South Dakota","SD"),
              ("Tennessee","TN"),
              ("Texas","TX"),
              ("Utah","UT"),
              ("Vermont","VT"),
              ("Virginia","VA"),
              ("Washington","WA"),
              ("West Virginia","WV"),
              ("Wisconsin","WI"),
              ("Wyoming","WY")]
    # temporary simple parse
    res = {}
    tmp = re.sub(r'[^a-zA-Z0-9, ]', '', raw_location.replace("B'",''))
    subbed = re.sub(r'[ ]+', ' ', tmp)
    parsed = str(subbed).split(',')    
    if len(parsed) > 1:
        res['city']    = parsed[0].strip()
        res['state']   = parsed[1].strip()
        res['country'] = 'USA'
        for pair in states:
            if res['state'] in pair:
                res['state'] = pair[1]
                return res
    else:
        for pair in states:
            if parsed[0].strip() in pair:
                res['city']    = 'Unknown'
                res['state']   = pair[1]
                res['country'] = 'USA'
                return res
            
    return None
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------





app = Flask(__name__)
#app.config.from_object('config')

@app.route('/')
def main(name="Home"):
    return render_template('index.html', name=name)

@app.route('/index')
def index(name="Home"):
    return render_template('index.html', name=name)

@app.route('/topic_modeling')
def topic_modeling():
    return render_template('topic_modeling.html')

@app.route('/maps')
def maps():
    return render_template('maps.html')

@app.route('/embeds')
def embeds():
    return render_template('embeds.html')





# AJAX data requests @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@app.route('/us_map_data')
def us_map_data():
    tbl = "Dxc_Technology"
    comp = request.args.get('company')
    if comp: 
        DB_cursor.execute("SELECT company_table FROM company_reviews.companies WHERE company_name = '{}' ".format(comp))
        result = DB_cursor.fetchone()
        tbl = result['company_table']
    req = ''' 
    SELECT 
        review_id               ,
        overall_review_score    ,
        job_work_life_balance   ,
        compensation_benefits   ,
        job_security_advancement,
        management              ,
        job_culture             ,
        poster_role             ,
        review_title            ,
        poster_status           ,
        poster_location         ,
        post_date 
    FROM indeed.`{}`
    '''.format(tbl)
    DB_cursor.execute(req)
    result = DB_cursor.fetchall()
        
    us_data = []
    for a_res in result:
        cpy = a_res.copy()
        geo = parse_location(a_res['poster_location'].upper())
        if geo:
            cpy['country'] = 'USA'
            cpy['city']    = geo['city']
            cpy['state']   = geo['state']
            us_data.append(cpy)
            
    #print(us_data)
    return json.dumps(us_data, default=str)

@app.route('/company_names')
def company_names():
    DB_cursor.execute("SELECT company_name FROM company_reviews.companies")
    result = DB_cursor.fetchall()
    cmp_list = []
    for a_res in result:
        cmp_list.append(a_res['company_name'])
    return json.dumps(cmp_list, default=str)

@app.route('/w2v')
def w2v():
    word = request.args.get('word')
    return


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
