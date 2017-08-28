# Topic modeling using Non-negative matrix factorization and Latent Dirichlet allocation

from sklearn.decomposition           import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

def display_topics(model, feature_names, no_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print ("Topic %d:" % (topic_idx)) 
        print (" ".join([feature_names[i]
            for i in topic.argsort()[:-no_top_words - 1:-1]]))

NUM_FEATURES = 1000
NUM_TOPICS   = 15

no_top_words = 10
#display_topics(nmf, tfidf_feature_names, no_top_words)
#display_topics(lda, tf_feature_names, no_top_words)

def NMF(content):
    global NUM_FEATURES; global NUM_TOPICS  
    # Convert a collection of raw documents to a matrix of TF-IDF features.
    # Equivalent to CountVectorizer followed by TfidfTransformer.
    # tf–idf - term frequency–inverse document frequency
    tfidf_vectorizer = TfidfVectorizer(max_features=no_features, max_df=0.95, min_df=2, stop_words='english')
    # Learn vocabulary and idf, return term-document matrix.
    tfidf_term_doc = tfidf_vectorizer.fit_transform(documents)
    # Array mapping from feature integer indices to feature name 
    tfidf_feature_names = tfidf_vectorizer.get_feature_names()
    # NMF (Non-negative matrix factorization)
    nmf = NMF(n_components=NUM_TOPICS, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf_term_doc)
    

def LDA(content):
    global NUM_FEATURES; global NUM_TOPICS;
    # Convert a collection of text documents to a matrix of token counts
    count_vectorizer = CountVectorizer(max_features=no_features, max_df=0.95, min_df=2, stop_words='english')
    # Learn the vocabulary dictionary and return term-document matrix.
    count_term_doc = tf_vectorizer.fit_transform(content)
    # Array mapping from feature integer indices to feature name
    count_feature_names = tf_vectorizer.get_feature_names()
    # LDA (Latent Dirichlet allocation)
    lda = LatentDirichletAllocation(n_topics=NUM_TOPICS, max_iter=5, learning_method='online', learning_offset=50.,random_state=0).fit(count_term_doc)

with open(FILE) as content_file:
    pass    
