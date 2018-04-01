from opinion_aspect_extraction import *
from sentiment_analysis import *
import pandas as pd
import numpy as np
import json
import os
import csv
import preprocessor as prep
import HTMLParser
import re
import sys


#if not sys.argv:
#    INPUT_FILE_NAME = '../Twitter/tweets'
#    OUTPUT_FILE_NAME = '../Twitter/twitter_reviews_to_opinions'
#    PRODUCT_FEATURES_FILENAME = 'product-features'
#    NUMBER_OF_RESULTS = 100
#    REVIEWS_COLUMN = 'text'
#    REVIEWS_COLUMN_TWO = ''
#    ID_FIELD = 'tweet_id'
#    ENGAGEMENT_FIELD = 'tweet_favorite_count'
#    PRE_PROCESS_TEXT = 'on'
#else:
INPUT_FILE_NAME = sys.argv[1]
OUTPUT_FILE_NAME = sys.argv[2]
PRODUCT_FEATURES_FILENAME = sys.argv[3]
NUMBER_OF_RESULTS = int(sys.argv[4])
REVIEWS_COLUMN = sys.argv[5]
PRE_PROCESS_TEXT = sys.argv[6]
ID_FIELD = sys.argv[7]
ENGAGEMENT_FIELD = sys.argv[8]
try:
    REVIEWS_COLUMN_TWO= sys.argv[9]
except:
    REVIEWS_COLUMN_TWO = False


output_file_columns = ['review_id', 'feature', 'opinion', 'sentiment', 'token', 'engagement']

#Load list of product features
features = pd.read_csv(PRODUCT_FEATURES_FILENAME+'.csv')
features_list = features['Feature'].tolist()
#features_list_stems = [find_stem_word(features_item) for features_item in features_list]


def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def preprocess_text(text):
    html_parser = HTMLParser.HTMLParser()
    text = html_parser.unescape(text)
    text = cleanhtml(text)
    text = text.decode('string_escape').decode('unicode_escape').encode('ascii','ignore')
    prep.set_options(prep.OPT.URL, prep.OPT.RESERVED, prep.OPT.EMOJI, prep.OPT.SMILEY)
    text = prep.clean(text)
    return text

reviews_to_features = pd.read_csv(INPUT_FILE_NAME+'.csv')
reviews_to_features = reviews_to_features.drop_duplicates(subset=[REVIEWS_COLUMN])
reviews_to_opinions = pd.DataFrame(columns = ['token', 'feature', 'opinion', 'sentiment'])

def extract_opinion_from_review(row, feature):
    tokens = sent_tokenize(row[REVIEWS_COLUMN])
    opinions = set()
    for token in tokens:
        [opinions.add(opinion) for opinion in extract_opinion(token, feature)]
        print opinions
    if opinions != []:
        return [np.repeat(row[REVIEWS_COLUMN],len(list(opinions))), list(opinions), np.repeat(feature,len(list(opinions)))]

def append_to_file(filename, dataframe):
    try:
        with open(filename, 'a') as f:
            if (os.stat(filename).st_size == 0):
                fields = output_file_columns
                writer = csv.writer(f)
                writer.writerow(fields) #writes field
            dataframe.to_csv(f, header=False)
    except IOError:
        print 'Could not open file'
    except:
        print 'Unexpected error writing to file ', filename

def save_last_read_location(filename, index):
    try:
        with open(filename, 'w') as f:
            f.write(str(index))
    except:
        print 'Unexpected error writing last read location to file ', filename

def read_last_saved_location(filename):
    try:
        with open(filename, 'r') as f:
            location = int(f.readline())
        return location
    except:
        print 'Unexpected error reading last saved location from file ', filename, '. Returning first location'
        return 0

def opinion_aspect_analysis(reviews_to_features, features_list, reviews_to_opinions):
    features_list = [find_stem_word(features_item) for features_item in features_list]
    last_read_location = read_last_saved_location(OUTPUT_FILE_NAME+'.txt')
    final_location = int(last_read_location) + NUMBER_OF_RESULTS
    if final_location > len(reviews_to_features):
        final_location = len(reviews_to_features)
    for i, row in reviews_to_features.iloc[last_read_location:final_location].iterrows():
        ###for feature in features_list:
        tokens = tokens2 = []
        try:
            if PRE_PROCESS_TEXT == 'on':
                tokens = sent_tokenize(preprocess_text(row[REVIEWS_COLUMN]))
            else:
                tokens = sent_tokenize(row[REVIEWS_COLUMN])
        except:
            print 'Error tokenizing ', REVIEWS_COLUMN
        try:
            if REVIEWS_COLUMN_TWO:
                if PRE_PROCESS_TEXT:
                    tokens2 = sent_tokenize(preprocess_text(row[REVIEWS_COLUMN_TWO]))
                else:
                    tokens2 = sent_tokenize(row[REVIEWS_COLUMN_TWO])
        except:
            print 'Error tokenizing ', REVIEWS_COLUMN_TWO
        tokens = tokens2 + tokens
        for token in tokens:
            print '\n', token
            words = word_tokenize(token)
            common_aspects = [word for word in words if find_stem_word(word) in features_list]
            for feature in common_aspects:
                extracted_aspect_opinions = set()
                extracted_aspect_opinions = extract_opinion(token, feature)
                if extracted_aspect_opinions:
                    for aspect, opinion in extracted_aspect_opinions:
                        print 'found opinion: ', opinion
                        print 'feature: ', feature
                        new_row = pd.DataFrame({'token': token, 'feature': aspect, 'opinion': opinion, 'sentiment': RateSentiment(token), 'review_id': row[ID_FIELD], 'engagement': row[ENGAGEMENT_FIELD]}, index = [i])
                        append_to_file(OUTPUT_FILE_NAME+'.csv', new_row)
                        reviews_to_opinions = reviews_to_opinions.append(new_row, ignore_index = False)
        print 'Saving file location: ', i
        save_last_read_location(OUTPUT_FILE_NAME+'.txt', i)
    return reviews_to_opinions
reviews_to_opinions = opinion_aspect_analysis(reviews_to_features, features_list, reviews_to_opinions)
#reviews_to_opinions.to_csv('reviews_to_opinions_pt1.csv')