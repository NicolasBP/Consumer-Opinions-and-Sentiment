#!/usr/bin/python

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import json
import pandas as pd
import os
import csv


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "XYZXYZXYZXYZXYZXYZXYZXYZXYZXYZXYZ"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

#def youtube_search(options):
def youtube_search(query, max_results):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    #q=options.q,
    q=query,
    part="id,snippet",
    #maxResults=options.max_results
    maxResults=max_results
  ).execute()
  
  
  videos_ids = []
  videos_titles = []
  channels = []
  playlists = []

  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      videos_ids.append(search_result["id"]["videoId"])
      videos_titles.append(search_result["snippet"]["title"].encode('unicode_escape'))
    elif search_result["id"]["kind"] == "youtube#channel":
      channels.append("%s (%s)" % (search_result["snippet"]["title"],
                                   search_result["id"]["channelId"]))
    elif search_result["id"]["kind"] == "youtube#playlist":
      playlists.append("%s (%s)" % (search_result["snippet"]["title"],
                                    search_result["id"]["playlistId"]))

  return pd.DataFrame({'video_id':videos_ids, 'title':videos_titles})


def get_comment_threads(youtube, video_data, query):
    results = youtube.commentThreads().list(
        part="snippet",
        videoId=video_data['video_id'],
        textFormat="plainText"
    ).execute()
    
    comments = pd.DataFrame(columns=('query','video_id', 'video_title', 'comment_timestamp', 'author', 'comment_text', 'likes'))
    
    for item in results["items"]:
        comment = item["snippet"]["topLevelComment"]
        timestamp = comment["snippet"]["publishedAt"]
        likes = comment["snippet"]["likeCount"]
        author = comment["snippet"]["authorDisplayName"].encode('unicode_escape')
        text = comment["snippet"]["textDisplay"].encode('unicode_escape')
        df = pd.DataFrame({'query':[query],'video_id':[video_data['video_id']], 'video_title':[video_data['title']], 'comment_timestamp':[timestamp], 'author':[author], 'comment_text':[text], 'likes':[likes]})
        comments = pd.concat([comments, df])
        #comments.append(df, ignore_index = True)
    
    return comments

#query = 'soylent'
#max_results = 10
#videos = youtube_search(query, max_results)
#
#
#youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
#    developerKey=DEVELOPER_KEY)
##comments = get_comment_threads(youtube, 'oKjWP_eHZwY')
#comments = pd.DataFrame(columns=('query','video_id', 'video_title', 'comment_timestamp', 'author', 'comment_text', 'likes'))
##comments = [pd.concat([comments, get_comment_threads(youtube, video_id)]) for video_id in videos['video_id']]
#
#
#for index,row in videos.iterrows():
#    try:
#        new_comments = get_comment_threads(youtube, row, query)
#        comments = pd.concat([comments, new_comments])
#    except:
#        pass


def collect_comments(queries, max_results):
    comments = pd.DataFrame(columns=('query','video_id', 'video_title', 'comment_timestamp', 'author', 'comment_text', 'likes'))
    for query in queries:
        videos = youtube_search(query, max_results)
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
            developerKey=DEVELOPER_KEY)
        for index,row in videos.iterrows():
            try:
                new_comments = get_comment_threads(youtube, row, query)
                comments = pd.concat([comments, new_comments])
            except:
                pass
    return comments



def json_to_csv(filename, dataframe):
    
    with open(filename, 'a') as f:
        if (os.stat(filename).st_size == 0):
            fields = ['query','video_id', 'video_title', 'comment_timestamp', 'author', 'comment_text', 'likes'] #field names
            writer = csv.writer(f)
            writer.writerow(fields) #writes field
        dataframe.to_csv(f, header=False)

#queries = ['meal replacement shakes -prank', 'meal replacement bars -prank', 'supplements', 'meal replacement supplement -bar -prank -shake', 'meal replacement smoothie -supplement -bar -shake -prank', 'meal replacement review -smoothie -supplement -bar -shake -prank']
#queries = ['shakeology', 'herbalife', '310 shake', 'slimfast', 'met rx meal replacement', 'GNC total lean shake', 'vega one shake']
#queries = ['eas advantedge', 'optim metabolic shake', 'ViSalus shakes', 'garden of life raw organic meal', 'delight fitmiss shake', 'CalNaturale shake', 'advocare meal replacement']
queries = ['sun warrior meal replacement', 'probar meal bar', 'naturade total soy meal replacement', 'orgain meal replacement', 'omnihealth meal replacement', 'atkins meal replacement bar', 'bariatric advantage meal replacement', 'ample foods meal replacement']
max_results = 10
comments = collect_comments(queries, max_results)
json_to_csv('youtube_comments.csv', comments)