from datetime    import datetime, date, time
from collections import Counter
from matplotlib  import pylab

import os
import re
import time
import random
import logging
import collections
import numpy as np
import configparser
import tensorflow as tf
from sklearn.manifold import TSNE


TXT_FILE_NAME = 'data.txt'
VOCAB_SIZE    = 5000
SOURCE_PATH   = os.path.dirname(os.path.abspath(__file__))
LOG_FILE_NAME = 'skip_gram_train_{}.log'.format(datetime.now().strftime("%Y-%m-%d_%H%M%S"))
LOGS_FOLDER   = 'logs'

# Right working directory
os.chdir(SOURCE_PATH)

# Set up logs
if not os.path.exists(LOGS_FOLDER):
    os.makedirs(LOGS_FOLDER)

logging.basicConfig(format='%(levelname)s\t%(asctime)s\t%(message)s', filename='{}/{}'.format(LOGS_FOLDER,LOG_FILE_NAME), datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
logging.info('Application has started')



with open(TXT_FILE_NAME) as txt_file:
    words = tf.compat.as_str(txt_file.read()).split()


pre_vocab = [['NULL', -1]] + Counter(words).most_common(VOCAB_SIZE - 1)

# Debug
#print(pre_vocab[:20])

# Because hash is faster when searching word's index
hash_map = dict()
for idx, (a_word, occurrence) in enumerate(pre_vocab):
    hash_map[a_word] = idx

data = []
nulls = 0

# Words with occurence rank higher than VOCAB_SIZE (rare words) will be replaces with Null
for a_word in words:
    if a_word in hash_map:
        a_word_idx = hash_map[a_word]
    else:
        a_word_idx = 0
        nulls += 1
    data.append(a_word_idx)

pre_vocab[0][1] = nulls

# Turn values into keys, and keys into values
key_reverse_hash_map = dict(zip(hash_map.values(), hash_map.keys())) 


data_index = 0
def generate_batch(batch_size, num_skips, skip_window):
    #---------------------------------- 
    global data_index
    assert batch_size % num_skips == 0
    assert num_skips <= 2 * skip_window
    #----------------------------------
    
    # Declare and init ---------------------------------------
    batch  = np.ndarray(shape=(batch_size), dtype=np.int32)
    labels = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
    slide_window_size = (2 * skip_window) +  1
    #                       ^                ^
    #       Words around the target       Center Word   
    buffer = collections.deque(maxlen=slide_window_size) 
    #---------------------------------------------------------
    
    # Populate the sliding window
    for _ in range(slide_window_size):
        buffer.append(data[data_index])
        data_index = (data_index + 1) % len(data)
   
    for i in range(batch_size // num_skips):
        target = skip_window  # target label at the center of the buffer
        targets_to_avoid = [ skip_window ]
        for j in range(num_skips):
            while target in targets_to_avoid:
                target = random.randint(0, slide_window_size - 1)
            targets_to_avoid.append(target)
            batch [i * num_skips + j   ] = buffer[skip_window]
            labels[i * num_skips + j, 0] = buffer[target]
        buffer.append(data[data_index])
        data_index = (data_index + 1) % len(data)
    return batch, labels

# Debug
#print('data:', [key_reverse_hash_map[di] for di in data[:8]])

#--------------------------------------------------------------------------------
batch_size = 128
embedding_size = 128 # Dimension of the embedding vector.
skip_window = 3 # How many words to consider left and right.
num_skips = 2 # How many times to reuse an input to generate a label.
# We pick a random validation set to sample nearest neighbors. here we limit the
# validation samples to the words that have a low numeric ID, which by
# construction are also the most frequent. 
valid_size     = 16 # Random set of words to evaluate similarity on.
valid_window   = 100 # Only pick dev samples in the head of the distribution.
num_sampled    = 64 # Number of negative examples to sample.
valid_examples = np.array(
    random.sample( range(valid_window), valid_size )
)
#--------------------------------------------------------------------------------

# Daddy in da house
graph = tf.Graph()

with graph.as_default(), tf.device('/gpu:0'): 
    # Input data
    train_dataset = tf.placeholder(tf.int32, shape=[batch_size])
    train_labels  = tf.placeholder(tf.int32, shape=[batch_size,1])
    valid_dataset = tf.constant(valid_examples, dtype=tf.int32)

    # Variables
    embeddings = tf.Variable(
        tf.random_uniform(  [VOCAB_SIZE, embedding_size], -1.0, 1.0  )
    ) # V x N
    softmax_weights = tf.Variable(
        tf.truncated_normal([VOCAB_SIZE, embedding_size], stddev=1.0 / np.sqrt(embedding_size))
    ) # V x N
    softmax_biases = tf.Variable(tf.zeros([VOCAB_SIZE]))
    

    # Model.
    # Look up embeddings for inputs.
    embed = tf.nn.embedding_lookup(embeddings, train_dataset)
    # Compute the softmax loss, using a sample of the negative labels each time.
    
    # Debug
    print("softmax_weights {}".format(softmax_weights)) 
    print("softmax_biases  {}".format(softmax_biases))
    print("embed           {}".format(embed))
    print("train_labels    {}".format(train_labels))
    print("num_sampled     {}".format(num_sampled))
    print("VOCAB_SIZE      {}".format(VOCAB_SIZE))
    
    
    loss = tf.reduce_mean(
        tf.nn.sampled_softmax_loss(
            weights=softmax_weights, 
            biases=softmax_biases, 
            inputs=embed,
            labels=train_labels, 
            num_sampled=num_sampled, 
            num_classes=VOCAB_SIZE
        )
    )

    # Optimizer.
    optimizer = tf.train.AdagradOptimizer(1.0).minimize(loss)
    
    # Compute the similarity between minibatch examples and all embeddings.
    # We use the cosine distance:
    norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keep_dims=True))
    normalized_embeddings = embeddings / norm
    valid_embeddings = tf.nn.embedding_lookup(normalized_embeddings, valid_dataset)
    similarity = tf.matmul(valid_embeddings, tf.transpose(normalized_embeddings))

# Create a saver.
saver = tf.train.Saver([embeddings,softmax_weights,softmax_biases])

num_steps = 1000001
with tf.Session(
    graph=graph, 
    config=tf.ConfigProto(
        allow_soft_placement=True, 
        log_device_placement=True
    )
) as session:
    tf.global_variables_initializer().run()
    print('Initialized')
    average_loss = 0
    for step in range(num_steps):
        batch_data, batch_labels = generate_batch(batch_size, num_skips, skip_window)
        feed_dict = {
            train_dataset : batch_data, 
            train_labels : batch_labels
        }
        _, l = session.run([optimizer, loss], feed_dict=feed_dict)
        average_loss += l
        if step % 2000 == 0:
            if step > 0:
                average_loss = average_loss / 2000
            # The average loss is an estimate of the loss over the last 2000 batches.
            print('Average loss at step %d: %f' % (step, average_loss))
            average_loss = 0
        # note that this is expensive (~20% slowdown if computed every 500 steps)
        if step % 10000 == 0:
            # Save the progress
            saver.save(session, 'saved_session.model', global_step=step)
            sim = similarity.eval()
            for i in range(valid_size):
                valid_word = key_reverse_hash_map[valid_examples[i]]
                top_k = 8 # number of nearest neighbors
                nearest = (-sim[i, :]).argsort()[1:top_k+1]
                log = 'Nearest to %s:' % valid_word
                for k in range(top_k):
                    close_word = key_reverse_hash_map[nearest[k]]
                    log = '%s %s,' % (log, close_word)
                print(log)
    final_embeddings = normalized_embeddings.eval()


num_points = 400

tsne = TSNE(perplexity=30, n_components=2, init='pca', n_iter=5000)
two_d_embeddings = tsne.fit_transform(final_embeddings[1:num_points+1, :])

def plot(embeddings, labels):
    assert embeddings.shape[0] >= len(labels), 'More labels than embeddings'
    pylab.figure(figsize=(15,15))  # in inches
    for i, label in enumerate(labels):
        x, y = embeddings[i,:]
        pylab.scatter(x, y)
        pylab.annotate(label, xy=(x, y), xytext=(5, 2), textcoords='offset points',
                     ha='right', va='bottom')
    pylab.show()

words = [key_reverse_hash_map[i] for i in range(1, num_points+1)]
plot(two_d_embeddings, words)

print("END!!")
