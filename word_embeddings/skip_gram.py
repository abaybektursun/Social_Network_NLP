from collections import Counter

import re
import random
import collections
import numpy as np
import tensorflow as tf


TXT_FILE_NAME = 'text8'
VOCAB_SIZE    = 10000

with open(TXT_FILE_NAME) as txt_file:
    words = tf.compat.as_str(txt_file.read()).split()

#TODO remove meaningless common words: the, and, a, ect.

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
    buffer = collections.deque(maxlen=slide_window_size) 
    batch  = np.ndarray(shape=(batch_size), dtype=np.int32)
    labels = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
    slide_window_size = (2 * skip_window) +  1
    #                       ^                ^
    #       Words around the target       Target Word   
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

print('data:', [key_reverse_hash_map[di] for di in data[:8]])

for num_skips, skip_window in [(2, 1), (4, 2)]:
    data_index = 0
    batch, labels = generate_batch(batch_size=8, num_skips=num_skips, skip_window=skip_window)
    print('\nwith num_skips = %d and skip_window = %d:' % (num_skips, skip_window))
    print('    batch:', [key_reverse_hash_map[bi] for bi in batch])
    print('    labels:', [key_reverse_hash_map[li] for li in labels.reshape(8)])





