import json
import sys
import os

ORIGINAL_FILE = "Hewlett-Packard-Enterprise_reviews.json" 
TRANSLTD_FILE = "TRANSLATED_" + ORIGINAL_FILE

def printtt(t1,t2):
    print("------------------------------------------------------------------------------------")
    print(  "Original: {} \nTranslated: {}".format(t1, t2)  )
    print("------------------------------------------------------------------------------------")


with open(ORIGINAL_FILE) as original_f, \
     open(TRANSLTD_FILE) as trans_f:
    orig  = json.load(original_f)
    trans = json.load(trans_f)
    for idx in range(100):
        if orig[idx]["review_text"] != trans[idx]["review_text"]: 
            printtt(orig[idx]["review_text"], trans[idx]["review_text"])

        if orig[idx]["pros"]        != trans[idx]["pros"]:
            printtt(orig[idx]["pros"], trans[idx]["pros"])

        if orig[idx]["cons"]        != trans[idx]["cons"]:
            printtt(orig[idx]["cons"], trans[idx]["cons"])
        
        
        
    
    

