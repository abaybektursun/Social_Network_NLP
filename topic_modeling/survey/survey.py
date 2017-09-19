# Topic modeling using Non-negative matrix factorization and Latent Dirichlet allocation

from sklearn.decomposition           import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

import chardet
import json
import csv

SURVEY_FILE_NAME  = "EPO_Comments.csv"
SURVEY2_FILE_NAME = "EPO_Comments_2.csv"

def extract(model, feature_names, no_top_words):
    clusters = []
    for topic_idx, topic in enumerate(model.components_):
        features = []
        # print ("Cluster of Topics %d:" % (topic_idx)) 
        for a_component in [feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]:
            features.append({"name": a_component})
        clusters.append({"name":"Cluster {}".format(topic_idx) ,"children":features})
    return clusters

NUM_FEATURES = 1000
NUM_TOPICS   = 5


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

probabilities = []    
def LDA(content):
    global NUM_FEATURES; global NUM_TOPICS; global probabilities;
    # Convert a collection of text documents to a matrix of token counts
    count_vectorizer = CountVectorizer(max_features=NUM_FEATURES, max_df=0.95, min_df=2, stop_words='english')
    # Learn the vocabulary dictionary and return term-document matrix.
    count_term_doc = count_vectorizer.fit_transform(content)
    # Array mapping from feature integer indices to feature name
    count_feature_names = count_vectorizer.get_feature_names()
    # LDA (Latent Dirichlet allocation)
    lda = LatentDirichletAllocation(n_components=NUM_TOPICS, max_iter=5, learning_method='online', learning_offset=50.,random_state=0).fit(count_term_doc)
    no_top_words = 5
    probabilities = lda.transform(count_term_doc).tolist()
    return extract(lda, count_feature_names, no_top_words)

with open(SURVEY_FILE_NAME) as content_file:
    responses = []
    reader = csv.reader(content_file)
    for row in reader:
        if row[1]: responses.append(row[1])
    LDA_clusters = LDA(responses)
# Create CSV and json
with open('PROB_'+SURVEY_FILE_NAME,'w+') as out_file, open('TOPICS_'+SURVEY_FILE_NAME.replace('csv','json'),'w+') as jf:
    writer = csv.writer(out_file, quoting=csv.QUOTE_ALL)
    for idx, a_resp in enumerate(responses):
        writer.writerow([a_resp]+probabilities[idx])
    json.dump(LDA_clusters,jf, indent=4)

#-----------------------------------------------------------------------------------------------------------------------------
with open(SURVEY2_FILE_NAME,'rb') as f: result = chardet.detect(f.read())
with open(SURVEY2_FILE_NAME, encoding=result['encoding']) as content_file:
    responses = []
    reader = csv.reader(content_file)
    for row in reader:
        if row[1]: responses.append(row[1])
    LDA_clusters = LDA(responses)
# Create CSV
with open('PROB_'+SURVEY2_FILE_NAME,'w+') as out_file, open('TOPICS_'+SURVEY2_FILE_NAME.replace('csv','json'),'w+') as jf:
    writer = csv.writer(out_file, quoting=csv.QUOTE_ALL)
    for idx, a_resp in enumerate(responses):
        writer.writerow([a_resp]+probabilities[idx])
    json.dump(LDA_clusters,jf, indent=4)

