import httplib2
import json
import apiclient.discovery
import pandas as pd
import csv
import os
from nltk import clean_html
from BeautifulSoup import BeautifulSoup

#q = "Tim O'Reilly"

API_KEY = 'XYZXYZXYZXYZXYZXYZXYZXYZXYZXYZ'

service = apiclient.discovery.build('plus', 'v1', http=httplib2.Http(), developerKey=API_KEY)

#people_feed = service.people().search(query=q).execute()

#print json.dumps(people_feed['items'], indent=1)

def cleanHtml(html):
    if html == "": return ""
    soup = BeautifulSoup(html)
    return soup.prettify()





the_query = 'herbalife'
activities_resource = service.activities()
activities_document = activities_resource.search( \
    maxResults=20,orderBy='best',query=the_query).execute()
print activities_document
posts_df = item_df = pd.DataFrame(columns = ('id', 'date_published', 'author', 'author_id', 'title', 
                                    'reshares', 'replies', 'plusoners', 'content', 'attachment_content', 'query'))

index = 0
if 'items' in activities_document:
  for activity in activities_document['items']:
    if activity['verb'] == 'post':
        #print activity['id'], activity['object']['content']
        posts_df.set_value(index, 'reshares', activity['object']['resharers']['totalItems'])
        #print 'reshares: ', activity['object']['resharers']['totalItems']
        #item_df['attachment_content'] = activity['object']['attachments'][0]['content']
        try:
            posts_df.set_value(index, 'attachment_content', activity['object']['attachments'][0]['content'].encode('unicode_escape'))
        except:
            posts_df.set_value(index, 'attachment_content', '')
        #print 'attachment_content: ', activity['object']['attachments'][0]['content'].encode('unicode_escape')
        #item_df['content'] = activity['object']['content']
        posts_df.set_value(index, 'content', cleanHtml(activity['object']['content'].encode('unicode_escape')))
        #print 'content: ', activity['object']['content'].encode('unicode_escape')
        #item_df['plusoners'] = activity['object']['plusoners']['totalItems']
        posts_df.set_value(index, 'plusoners', activity['object']['plusoners']['totalItems'])
        #print 'plusoners: ', activity['object']['plusoners']['totalItems']
        #item_df['replies'] = activity['object']['replies']['totalItems']
        posts_df.set_value(index, 'replies', activity['object']['replies']['totalItems'])
        #print 'replies: ', activity['object']['replies']['totalItems']
        #item_df['replies'] = activity['title']
        posts_df.set_value(index, 'title', activity['title'].encode('unicode_escape'))
        #print 'title: ', activity['title'].encode('unicode_escape')
        #item_df['replies'] = activity['actor']['displayName']
        posts_df.set_value(index, 'author', activity['actor']['displayName'].encode('unicode_escape'))
        posts_df.set_value(index, 'author_id', activity['actor']['id'])
        #item_df['verb'] = activity['verb']
        #posts_df.set_value(index, 'verb', activity['verb'])
        #item_df['date_published'] = activity['published']
        posts_df.set_value(index, 'date_published', activity['published'])
        #item_df['id'] = activity['id']
        posts_df.set_value(index, 'id', activity['id'])
        posts_df.set_value(index, 'query', the_query)
        print posts_df
        #posts_df = pd.concat([posts_df, item_df])
        #posts_df = posts_df.append(item_df, ignore_index = True)
        index = index + 1

def json_to_csv(filename, dataframe):
    
    with open(filename, 'a') as f:
        if (os.stat(filename).st_size == 0):
            fields = ['index','id', 'date_published', 'author', 'author_id', 'title', 'reshares', 'replies', 'plusoners', 'content', 'attachment_content', 'query'] #field names
            writer = csv.writer(f)
            writer.writerow(fields) #writes field
        dataframe.to_csv(f, header=False)


json_to_csv('google_plus_activity.csv', posts_df)