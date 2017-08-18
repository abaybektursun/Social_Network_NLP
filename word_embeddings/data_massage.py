import glob
import sys
import csv
import re


common_words = []

with open('popular-both-first.txt') as openfile:
    common_words += openfile.read().split("\n")
with open('popular-last.txt') as openfile:
    common_words += openfile.read().split("\n")

common_words += ['which','when','can','time','into','some','them','other','than','then','also','back','two','how','first','way','even','because','any','these','day','most','all','just','not','as','up','there','the','a','an','and','or','if','that','so','this','year','one','our','his','her','my','their','your','its','to','of','in','for','on','with','at','by','from','out','over','after','but','about','I','it','he','you','they','we','she','me','him','us','what','who','be','have','would','get','could','see','look','come','give','say','do','will','go','make','know','take','use','work']


common_words = [x.lower() for x in common_words]
glob.glob("../fb_scrapper/data/*_page.csv")

#in_str   = sys.argv[1]
#page_ids = in_str.split(',')

page_ids = []
for a_path in glob.glob("../fb_scrapper/data/*_page.csv"):
    a_name = a_path.split('/')[-1]
    page_ids.append(a_name.split('_')[0])


def remove_common_words(string): 
    return ' '.join([item for item in string.lower().split(' ') if item not in common_words]) + ' '

out_name = 'data.txt'
with open(out_name, 'w') as out_file:
    for page_id in page_ids:
        csv_name          = '../fb_scrapper/data/{}_page.csv'.format(page_id)
        csv_comments_name = '../fb_scrapper/data/{}_page_comments.csv'.format(page_id)
        with open(csv_name)          as csv_file, \
             open(csv_comments_name) as comments_csv_file:
            
            reader = csv.reader(csv_file)
            comment_reader = csv.reader(comments_csv_file)
            for row in reader:
                out_file.write( remove_common_words( re.sub("[^a-zA-Z]+"," ",re.sub(r'^https?:\/\/.*[\r\n]*', '', row[3], flags=re.MULTILINE))) )
            for row in comment_reader:
                out_file.write( remove_common_words( re.sub("[^a-zA-Z]+"," ",re.sub(r'^https?:\/\/.*[\r\n]*', '', row[3], flags=re.MULTILINE))) )
