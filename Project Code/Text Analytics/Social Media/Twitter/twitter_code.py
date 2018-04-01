# prepare for Python version 3x features and functions
from __future__ import division, print_function, absolute_import

import twitter  # work with Twitter APIs
import io
import os
import json  # methods for working with JSON data
import csv
import pandas as pd
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx  #module for plotting networks

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


windows_system = False  # set to True if this is a Windows computer
if windows_system:
    line_termination = '\r\n' # Windows line termination
if (windows_system == False):
    line_termination = '\n' # Unix/Linus/Mac line termination


# name for text file for review of results
full_text_filename = 'my_tweet_review_file.txt'  

#Function for authenticating api session    
def oauth_login():
    #Keys have been deleted. Replace with new keys to run applicatinon
    CONSUMER_KEY = 'XYZXYZXYZXYZXYZXYZXYZXYZXYZXYZXYZ'
    CONSUMER_SECRET = 'XYZXYZXYZXYZXYZXYZXYZXYZXYZXYZXYZ'
    OAUTH_TOKEN = 'XYZXYZXYZXYZXYZXYZXYZXYZXYZXYZXYZ'
    OAUTH_TOKEN_SECRET = 'XYZXYZXYZXYZXYZXYZXYZXYZXYZXYZXYZ'
    
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                               CONSUMER_KEY, CONSUMER_SECRET)
    
    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api


#Gets the users with most followers. Argument is an object containing the data returned by the Twitter API
def get_most_popular_users(statuses):
    #Get a tuple of screen names and number of followers
    screen_names_followers = [ (status["user"]["screen_name"], status["user"]["followers_count"]) for status in statuses ]
    
    df_screen_names_followers = pd.DataFrame(screen_names_followers)  #create a dataframe
    df_screen_names_followers.columns = ["screen_name", "followers_count"]  #rename columns
    df_screen_names_followers = df_screen_names_followers.drop_duplicates()
    top_users = df_screen_names_followers.sort("followers_count", ascending = 0) #sort in descending order
    top_users = top_users.head(5) #get top 5 users
    #Build a bar graph
    objects = list(top_users["screen_name"])
    y_pos = np.arange(len(objects))
    performance = list(top_users["followers_count"])
    
    plt.bar(y_pos, performance, align='center', alpha=0.5)
    plt.xticks(y_pos, objects)
    plt.ylabel('Followers')
    plt.title('Users')
    
    #save graph to file
    plt.savefig('Top_users.pdf', orientation = 'landscape', papertype = 'legal' )
    
    
    return top_users
    
#Get all tweet text and save it to a text file    
def get_tweets(statuses):   
    #extract text from each status object
    status_texts = [ status['text'] for status in statuses ]
    
    item_count = 0
    with open('status_texts.txt', 'w') as outfile: #write to an external file, line by line
        for dict_item in status_texts:
            outfile.write('Item index: ' + str(item_count) +\
                ' -----------------------------------------' + line_termination)
            # indent for pretty printing
            outfile.write(json.dumps(dict_item, indent = 4))  
            item_count = item_count + 1
            if item_count < len(status_texts):
                outfile.write(line_termination)
                
    return status_texts

#Get user mentions related to the provided top_user list.
def get_user_mentions(statuses, top_users):
    #Extract pairs of user who was mentioned and user who posted the tweet.
    mentions = [ [ (status["user"]["screen_name"], user_mention["screen_name"]) for user_mention in status["entities"]["user_mentions"] ] for status in statuses ]
    
    mentions = pd.DataFrame(mentions)
    mentions1 = [mention for mention in mentions[0] if mention] #eliminate empty mentions
    mentions2 = [mention for mention in mentions[1] if mention]
    all_mentions = pd.DataFrame(mentions1 + mentions2) #consolidate all mentions into two columns in the dataframe
    all_mentions.columns = ['user', 'mentioned_by'] #rename the columns accordingly
    all_mentions = all_mentions.sort_values('user', ascending = True) #sort in alphabetical order by user
    popular_mentions = all_mentions[all_mentions['mentioned_by'].isin(top_users['screen_name'])] #filter all mentions to only those that are related to popular users
    #write pairs into a text file, line by line
    with open('mentions.txt', 'w') as outfile:
        outfile.write(line_termination)
        for row in popular_mentions.iterrows():
            outfile.write(row[1][0] + "," + row[1][1]) 
            outfile.write(line_termination + line_termination)
            
    return mentions

# creates a network graph and reports some network statistics 
def generate_network_graph():
    f = open('mentions.txt', 'rb')     
    g = nx.read_edgelist(f, create_using = nx.DiGraph(), delimiter = ',', nodetype = str)
    f.close()
    
    # print graph attributes
    print('This is a directed network/graph (True or False): ', g.is_directed())
    print('Number of nodes: ', nx.number_of_nodes(g))
    print('Number of edges: ', nx.number_of_edges(g))
    print('Network density: ', round(nx.density(g), 4))
    # determine the total number of links for the network 
    
    # plot the degree distribution 
    fig = plt.figure()
    nx.draw_networkx(g, node_size = 200, node_color = 'yellow', font_color='blue', edge_color = 'red', pos = nx.shell_layout(g))  
    
    plt.savefig('network.pdf', orientation = 'landscape', papertype = 'legal' )                      
                      
# -------------------------------------
# searching the REST API a la Russell (2014) section 9.4
def twitter_search(twitter_api, q, latitude, longitude, max_range, max_results, **kw):

    #search_results = twitter_api.search.tweets(q=q, geocode = "%f,%f,%dmi" % (latitude, longitude, max_range), count=100, **kw)
    search_results = twitter_api.search.tweets(q=q, lang='en', count=500, **kw)
    statuses = search_results['statuses']
    
    # Iterate through batches of results by following the cursor until we
    # reach the desired number of results, keeping in mind that OAuth users
    # can "only" make 180 search queries per 15-minute interval. 
    for _ in range(100): 
        try:
            next_results = search_results['search_metadata']['next_results']
        except KeyError, e: # No more results when next_results doesn't exist
            break
            
        # Create a dictionary from next_results, which has the following form:
        # ?max_id=313519052523986943&q=NCAA&include_entities=1
        kwargs = dict([ kv.split('=') 
                        for kv in next_results[1:].split("&") ])
        
        search_results = twitter_api.search.tweets(**kwargs)
        statuses += search_results['statuses']
        
        if len(statuses) > max_results: 
            break                  
                                                          
    return statuses




def save_json(filename, data):
    with io.open('{0}.json'.format(filename), 'w', encoding = 'utf-8') as f:
        f.write(unicode(json.dumps(data, ensure_ascii=False)))

def load_json(filename):
    with io.open('{0}.json'.format(filename), encoding = 'utf-8') as f:
        return f.read()


def json_to_csv(filename, query):
    data_json = open(filename, mode='r').read() #reads in the JSON file into Python as a string
    data_python = json.loads(data_json) #turns the string into a json Python object
    
    csv_out = open('tweets.csv', mode='a') #opens csv file
    writer = csv.writer(csv_out) #create the csv writer object
    
    if (os.stat("tweets.csv").st_size == 0):
        fields = ['created_at', 'tweet_id', 'query', 'coordinates', 'coordinates_type', 'country_code', 'place_full_name', 'retweet_count', 
                'text', 'in_reply_to_status_id_str', 'is_quote_status', 'tweet_favorite_count', 'user_description', 
                'user_fovourites_count', 'followers_count', 'friends_count', 
                'user_profile_location', 'time_zone'] #field names
        writer.writerow(fields) #writes field
    
    
    for line in data_python:
        try:
            coordinates = line.get('place').get('bounding_box').get('coordinates')
        except:
            coordinates = None
        try:
            coordinates_type = line.get('place').get('bounding_box').get('type')
        except:
            coordinates_type = None
        try:
            country_code = line.get('place').get('country_code')
        except:
            country_code = None
        try:
            place_full_name = line.get('place').get('full_name')
        except:
            place_full_name = None
        try:
            time_zone = line.get('user').get('time_zone').encode("utf-8")
        except:
            time_zone = None
            
        #writes a row and gets the fields from the json object
        #screen_name and followers/friends are found on the second level hence two get methods
        writer.writerow([line.get('created_at'),
                        line.get('id_str'),
                        query,
                        coordinates,
                        coordinates_type,
                        country_code,
                        place_full_name,
                        line.get('retweet_count'),
                        line.get('text').encode('unicode_escape'), #unicode escape to fix emoji issue
                        line.get('in_reply_to_status_id_str'),
                        line.get('is_quote_status'),
                        line.get('favorite_count'),
                        line.get('user').get('description').encode('unicode_escape'),
                        line.get('user').get('fovourites_count'),
                        line.get('user').get('followers_count'),
                        line.get('user').get('friends_count'),
                        line.get('user').get('location'),
                        time_zone])
    
    csv_out.close()


#authenticate session
twitter_api = oauth_login()   
print(twitter_api)  # verify the connection
latitude = 37.75619	# geographical centre of search
longitude = -122.44262	# geographical centre of search
max_range = 5.6327 			# search range in kilometres
q = "herbalife"  # the query
#search twitter
#results = twitter_search(twitter_api, q, geolocation, max_results = 1500) 
results = twitter_search(twitter_api, q, latitude, longitude, max_range, max_results = 1500)
save_json('tweets', results)
json_to_csv('tweets.json', q)
#get text tweets
#txt_tweets = get_tweets(results)
#find most popular users
#top_users = get_most_popular_users(results)  
#get mentions including popular users
#mentions = get_user_mentions(results, top_users)
#generate network graph using mentions
#generate_network_graph()







# examping the results object... should be list of dictionary objects
print('\n\ntype of results:', type(results)) 
print('\nnumber of results:', len(results)) 

                     
# -------------------------------------
# working with text file for reviewing multiple JSON objects
# this text file will show the full contents of each tweet
# results is a list of dictionary items obtained from twitter
# these functions assume that each dictionary item
# is written as group of lines printed with indentation
item_count = 0  # initialize count of objects dumped to file
with open(full_text_filename, 'w') as outfile:
    for dict_item in results:
        outfile.write('Item index: ' + str(item_count) +\
             ' -----------------------------------------' + line_termination)
        # indent for pretty printing
        outfile.write(json.dumps(dict_item, indent = 4))  
        item_count = item_count + 1
        if item_count < len(results):
             outfile.write(line_termination)  # new line between items  
        






