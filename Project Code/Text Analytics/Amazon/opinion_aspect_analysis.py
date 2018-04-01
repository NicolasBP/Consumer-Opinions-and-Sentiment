from opinion_aspect_extraction import *
from sentiment_analysis import *
import pandas as pd
import numpy as np
import json
import os
import csv

REVIEWS_COLUMN = 'reviewText'

reviews = []
line_number = 0
with open('reviews_Health_and_Personal_Care_5.json') as f:
    for line in f:
        if line_number < 501:
            reviews.append(json.loads(line))
            line_number = line_number + 1
        else:
            break

reviews_df = pd.DataFrame(reviews)

reviews_df.to_csv('amazon_reviews_sample.csv')

#Load list of product features
features = pd.read_csv('product-features part3.csv')
features_list = features['Feature'].tolist()

###Load list of opinion words
###opinion_words = pd.read_csv('opinion_words.csv')
###opinion_words_list = opinion_words['Opinion'].tolist()

def filter_reviews_by_list(word_list, reviews_df):
    pattern = '|'.join(word_list)
    features_reviews_df = reviews_df[reviews_df.reviewText.str.contains(pattern)]
    return features_reviews_df

features_reviews_df = filter_reviews_by_list(features_list, reviews_df)

###features_df  = pd.DataFrame(columns = features_list)
###print features_df

###reviews_to_features = pd.concat([features_reviews_df, features_df], axis=1)
###print reviews_to_features.head(2)

#def filter_reviews_by_feature(col, x):
###def find_instance_of_word(col, x):
###    index = x.reviewText.find(col)
###    x[col] = index
###    return x[col]

###for feature in features_list:
###    reviews_to_features[feature] = reviews_to_features[['reviewText',feature]].apply(lambda x: find_instance_of_word(feature, x), axis = 1)
    #[reviews_to_features[['reviewText',feature]].apply(lambda x: filter_reviews_by_feature(col, x), axis = 1) for col in features_list]
#reviews_to_features_result.to_csv('reviews_to_features_result.csv')
#reviews_to_features_result_df = pd.DataFrame(reviews_to_features_result)
reviews_to_features = pd.read_csv('meal_replacement_product_reviews.csv')
#reviews_to_features = reviews_to_features.head(1)
##print reviews_to_features['reviewText'].head(2)
##len(reviews_to_features)
#reviews_to_features.to_csv('reviews_to_features_result.csv')

#extract_opinion("iPod is the best mp3 player", 'iPod')

reviews_to_opinions = pd.DataFrame(columns = ['token', 'feature', 'opinion', 'sentiment'])
#reviews_to_opinions['reviewText'] = reviews_to_features['reviewText']



def extract_opinion_from_review(row, feature):
    tokens = sent_tokenize(row[REVIEWS_COLUMN])
    opinions = set()
    for token in tokens:
        #[opinions.add(value1) for (value1, value2) in extract_opinion(token, feature)]
        [opinions.add(opinion) for opinion in extract_opinion(token, feature)]
        print opinions
    if opinions != []:
        #return {'reviewText': np.repeat(row('reviewText'),len(list(opinions))), 'opinion':list(opinions),'feature':np.repeat(feature,len(list(opinions)))}
        return [np.repeat(row['reviewText'],len(list(opinions))), list(opinions), np.repeat(feature,len(list(opinions)))]

def append_to_file(filename, dataframe):
    try:
        with open(filename, 'a') as f:
            if (os.stat(filename).st_size == 0):
                fields = ['index','asin', 'feature', 'helpful', 'opinion', 'overall', 'sentiment', 'token', 'unixReviewTime'] #field names
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
    last_read_location = read_last_saved_location('reviews_to_opinions.txt')
    for i, row in reviews_to_features.iloc[last_read_location:2800].iterrows():
        ###for feature in features_list:
        tokens = summary = []
        try:
            tokens = sent_tokenize(row[REVIEWS_COLUMN])
        except:
            print 'Error tokenizing ', REVIEWS_COLUMN
        try:
            summary = sent_tokenize(row['summary'])
        except:
            print 'Error tokenizing summary'
        tokens = summary + tokens
        for token in tokens:
            print token, '\n'
            words = word_tokenize(token)
            common_aspects = [word for word in words if find_stem_word(word) in features_list]
            for feature in common_aspects:
                ###if find_stem_word(feature) in [find_stem_word(word) for word in words]:
                extracted_aspect_opinions = set()
                #[opinions.add(value1) for (value1, value2) in extract_opinion(token, feature)]
                extracted_aspect_opinions = extract_opinion(token, feature)
                if extracted_aspect_opinions:
                    #[aspect_opinions.add((aspect, opinion)) for (aspect,opinion) in extracted_aspect_opinions]
                    #if len(extracted_aspect_opinions):
                    for aspect, opinion in extracted_aspect_opinions:
                        print 'found opinion: ', opinion
                        print 'feature: ', feature
                        new_row = pd.DataFrame({'token': token, 'feature': aspect, 'opinion': opinion, 'sentiment': RateSentiment(token), 'asin': row['asin'], 'helpful': row['helpful'], 'overall': row['overall'], 'unixReviewTime': row['unixReviewTime']}, index = [i])
                        append_to_file('reviews_to_opinions.csv', new_row)
                        reviews_to_opinions = reviews_to_opinions.append(new_row, ignore_index = False)
            #reviews_to_opinions.append(pd.DataFrame(extract_opinion_from_review(row, feature)), ignore_index = False)
            #reviews_to_opinions.append(pd.DataFrame(reviews_to_opinions.apply(lambda x: extract_opinion_from_review(x, feature), axis = 1)), ignore_index = False)
        print 'Saving file location: ', i
        save_last_read_location('reviews_to_opinions.txt', i)
    return reviews_to_opinions
reviews_to_opinions = opinion_aspect_analysis(reviews_to_features, features_list, reviews_to_opinions)
#reviews_to_opinions.to_csv('reviews_to_opinions_pt1.csv')