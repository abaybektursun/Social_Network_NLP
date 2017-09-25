# Topic modeling using Non-negative matrix factorization and Latent Dirichlet allocation

from sklearn.decomposition           import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from datetime                        import datetime, date, time


import pymysql.cursors
import configparser
import logging
import pickle
import json
import time
import sys
import os
import re

####################################################################################################################################
LOG_FILE_NAME = 'topics_{}.log'.format(datetime.now().strftime("%Y-%m-%d_%H%M%S"))
LOGS_FOLDER   = 'logs'

# Set up logs
if not os.path.exists(LOGS_FOLDER):
    os.makedirs(LOGS_FOLDER)
logging.basicConfig(format='%(levelname)s\t%(asctime)s\t%(message)s', filename='{}/{}'.format(LOGS_FOLDER,LOG_FILE_NAME), datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
logging.info('Application has started')

# Database
dbconfigs = configparser.ConfigParser()
dbconfigs.read('../msql.dbcredentials')
try: connection   = pymysql.connect(
    host     = dbconfigs['default']['HOST'],
    user     = dbconfigs['default']['USER'],
    password = dbconfigs['default']['PASS'],
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
);
except Exception as ex: exit("Failed to connect to database", 2); logging.error(str(ex))
DB_cursor = connection.cursor()
####################################################################################################################################

def extract(model, feature_names, no_top_words):
    clusters = []
    for topic_idx, topic in enumerate(model.components_):
        features = []
        # print ("Cluster of Topics %d:" % (topic_idx)) 
        for a_component in [feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]:
            features.append({"name": a_component, "size": 4500})
        clusters.append({"name":"Cluster {}".format(topic_idx) ,"children":features})
    return clusters


def NMF(content):
    global NUM_FEATURES; global NUM_TOPICS  
    # Convert a collection of raw documents to a matrix of TF-IDF features.
    # Equivalent to CountVectorizer followed by TfidfTransformer.
    # tf–idf - term frequency–inverse document frequency
    tfidf_vectorizer = TfidfVectorizer(max_features=NUM_FEATURES, max_df=0.95, min_df=2, stop_words='english')
    # Learn vocabulary and idf, return term-document matrix.
    tfidf_term_doc = tfidf_vectorizer.fit_transform(content)
    # Array mapping from feature integer indices to feature name 
    tfidf_feature_names = tfidf_vectorizer.get_feature_names()
    # NMF (Non-negative matrix factorization)
    nmf = NMF(n_components=NUM_TOPICS, init='nndsvd', random_state=1, alpha=.1, l1_ratio=.5).fit(tfidf_term_doc)
    no_top_words = 10
    return extract(nmf, tfidf_feature_names, no_top_words)
    

def LDA(content):
    global NUM_FEATURES; global NUM_TOPICS;
    # Convert a collection of text documents to a matrix of token counts
    count_vectorizer = CountVectorizer(max_features=NUM_FEATURES, max_df=0.95, min_df=2, stop_words='english')
    # Learn the vocabulary dictionary and return term-document matrix.
    count_term_doc = count_vectorizer.fit_transform(content)
    # Array mapping from feature integer indices to feature name
    count_feature_names = count_vectorizer.get_feature_names()
    # LDA (Latent Dirichlet allocation)
    lda = LatentDirichletAllocation(n_components=NUM_TOPICS, max_iter=5, learning_method='online', learning_offset=50.,random_state=0).fit(count_term_doc)
    no_top_words = 10
    return extract(lda, count_feature_names, no_top_words)

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
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
DB_cursor.execute("SELECT * FROM company_reviews.companies")
result   = DB_cursor.fetchall()
cmp_list = []
for a_res in result:
    cmp_list.append(a_res['company_table'])

NUM_FEATURES = 1000
NUM_TOPICS   = 5
for a_cmp in cmp_list:
    DB_cursor.execute("SELECT * FROM indeed." + a_cmp)
    result   = DB_cursor.fetchall() 
    with open('topics_data/topics_'+a_cmp.lower()+".json","w") as json_out:
        pros = []; cons = []; reviews = [];
        for a_review in result:
            if parse_location(a_review['poster_location'].upper()):
                if a_review['pros'] and '\\' not in a_review['pros']: pros.append(a_review['pros'])
                if a_review['cons'] and '\\' not in a_review['cons']: cons.append(a_review['cons'])
                if a_review['review_text'] and '\\' not in a_review['review_text']: reviews.append(a_review['review_text'])
        pro_cluster = LDA(pros)
        con_cluster = LDA(cons)
        rev_cluster = LDA(reviews)
         
        json.dump({
            "name":a_cmp.replace('_',' '), 
            "children": [{"name":"Cons","children":con_cluster}, {"name":"Pros","children":pro_cluster}, {"name":"General Review","children":rev_cluster}]
        }, json_out, indent=4)
    
# Housekeeping ############################################################################################
DB_cursor.close()
connection.close()
