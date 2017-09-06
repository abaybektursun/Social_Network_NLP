# Topic modeling using Non-negative matrix factorization and Latent Dirichlet allocation

from sklearn.decomposition           import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

import json

def extract(model, feature_names, no_top_words):
    clusters = []
    for topic_idx, topic in enumerate(model.components_):
        features = []
        # print ("Cluster of Topics %d:" % (topic_idx)) 
        for a_component in [feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]:
            features.append({"name": a_component, "size": 4500})
        clusters.append({"name":"Cluster {}".format(topic_idx) ,"children":features})
    return clusters

FILE_NAME =  "Hewlett-Packard-Enterprise_reviews.json"
FILE_PATH =  "../indeed_scrapper/" + FILE_NAME

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

with open(FILE_PATH) as content_file, open("graph.jon","w") as json_out:
    json_content = json.loads(content_file.read())
    pros = []; cons = []; reviews = [];
    for a_review in json_content:
        if a_review['pros']: pros.append(a_review['pros'])
        if a_review['cons']: cons.append(a_review['cons'])
        if a_review['review_text']: reviews.append(a_review['review_text'])
    pro_cluster = LDA(pros)
    con_cluster = LDA(cons)
    rev_cluster = LDA(reviews)
     
    json.dump({
        "name":"Hewlett Packard Enterprise", 
        "children": [{"name":"Cons","children":con_cluster}, {"name":"Pros","children":pro_cluster}, {"name":"General Review","children":rev_cluster}]
    }, json_out, indent=4)
