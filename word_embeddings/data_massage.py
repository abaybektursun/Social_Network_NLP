import sys
import csv
import re

"""
post['id'],
post.get('from','')['id'],
post.get('from','')['name'],
post.get('message',''),
post.get('link', ''),
post.get('tags',''),
post.get('object_attachment',''),
post['created_time'],
post.get('description',''),
post['reactions_count']['reactions_like'    ]['summary']['total_count'],
post['reactions_count']['reactions_love'    ]['summary']['total_count'],
post['reactions_count']['reactions_wow'     ]['summary']['total_count'],
post['reactions_count']['reactions_haha'    ]['summary']['total_count'],
post['reactions_count']['reactions_sad'     ]['summary']['total_count'],
post['reactions_count']['reactions_angry'   ]['summary']['total_count'],
post['reactions_count']['reactions_thankful']['summary']['total_count']


post['id'],
comment['id'],
comment['created_time'],
comment['from'].get('name',''),
comment['from']['id'],
comment['message']
"""

in_str   = sys.argv[1]
page_ids = in_str.split(',')

out_name = 'data.txt'
with open(out_name, 'w') as out_file:
    for page_id in page_ids:
        csv_name          = '../fb_scrapper/{}_page.csv'.format(page_id)
        csv_comments_name = '../fb_scrapper/{}_page_comments.csv'.format(page_id)
        with open(csv_name)          as csv_file, \
             open(csv_comments_name) as comments_csv_file
            reader = csv.reader(csv_file)
            comment_reader = csv.reader(comments_csv_file)
            for row in reader:
                out_file.write(re.sub("[^a-zA-Z]+"," ",row[3])+' ')
            for row in comment_reader:
                out_file.write(re.sub("[^a-zA-Z]+"," ",row[5])+' ')
