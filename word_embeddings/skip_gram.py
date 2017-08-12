from collections import Counter

import re
import tensorflow as tf


TXT_FILE_NAME = 'text8'
VOCAB_SIZE    = 10000

with open(TXT_FILE_NAME) as txt_file:
    words = tf.compat.as_str(txt_file.read()).split()

#TODO remove meaningless common words: the, and, a, ect.

pre_vocab = [('NULL', -1)] + Counter(words).most_common(VOCAB_SIZE - 1)

# Debug
#print(pre_vocab[:20])

# Because hash is faster when searching word's index
hash_map = dict()
for idx, (a_word, occurrence) in enumerate(pre_vocab):
    hash_map[a_word] = idx

data = []
nulls = 0

for a_word in words:
    if a_word in hash_map:
        a_word_idx = hash_map[a_word]
    else:
        a_word_idx = 0
        nulls += 1
    data.append(a_word_idx)

pre_vocab[0][1] = nulls
key_val_reverse_hash_map = dict(zip(dictionary.values(), dictionary.keys())) 


"""for word, _ in count:
    dictionary[word] = len(dictionary)
    print('{}, {}'.format(word, len(dictionary)))
"""




