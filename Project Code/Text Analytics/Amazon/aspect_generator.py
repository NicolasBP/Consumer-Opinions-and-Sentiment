from opinion_aspect_extraction import *
import pandas as pd
import nltk
from nltk import sent_tokenize
from nltk import word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.corpus import wordnet as wn

REVIEWS_COLUMN = 'reviewText'

reviews_to_features = pd.read_csv('meal_replacement_product_reviews_part2.csv')
#reviews_to_features = reviews_to_features.head(20)

#Load list of product features
features = pd.read_csv('product-features copy.csv')
features_list = features['Feature'].tolist()
features_list = [find_stem_word(features_item) for features_item in features_list]
#features_list = set(features['Feature'])

def find_new_aspects(review_text, features_list):
    extracted_aspects = set(features_list)
    #extracted_aspects = features_list
    tokens = sent_tokenize(review_text)
    new_features = set()
    for token in tokens:
        words = word_tokenize(token)
        words = set(words)
        #words = set([find_stem_word(word) for word in words])
        #if words.issubset(extracted_aspects):
        try:
            #common_aspects = words.intersection(set(features_list))
            common_aspects = [word for word in words if find_stem_word(word) in features_list]
            if common_aspects:
                print '\n##Common Aspects Found: ', common_aspects
                new_features = extract_aspects_from_aspects(token, common_aspects)
        except:
            print 'UnexpectedError extracting aspects'
            print 'Skipping sentence...'
            continue
        #new_features = {find_stem_word(new_feature) for new_feature in new_features}
        if not new_features.issubset(extracted_aspects):
            print 'Adding new aspects: ', new_features
            [extracted_aspects.add(new_feature) for new_feature in new_features]
            #find_new_aspects(token, list(extracted_aspects))
            #find_new_aspects(token, extracted_aspects)
    return extracted_aspects            
                    
def generate_aspects_from_aspects(reviews_to_features, features_list):           
    extracted_aspects = set()
    for i, row in reviews_to_features.iterrows():
        new_aspects = find_new_aspects(row[REVIEWS_COLUMN], features_list)
        [extracted_aspects.add(new_aspect) for new_aspect in new_aspects]
    return extracted_aspects

def find_synonyms(the_word, word_type):
    the_synsets = wn.synsets(the_word, pos=word_type)
    #return the_synsets
    #print noun_synsets
    if not the_synsets:
        return []
    else:
        the_lemmas = [l.name() for s in the_synsets for l in s.lemmas() if s.name().split('.')[1] == word_type and s.name().split('.')[2] == '01']
        return set(the_lemmas)

#print find_new_aspects('', features_list)
aspects = generate_aspects_from_aspects(reviews_to_features, features_list)
seed_aspects = set(features['Feature'])
all_aspects = seed_aspects.union(aspects)
#print aspects

aspects_df = pd.DataFrame({'Aspects': list(all_aspects)})
aspects_df.to_csv('generated_aspects.csv')


#set_aspects = features_list
#for aspect in aspects:
#    new_aspects = find_synonyms(aspect, 'n')
#    [set_aspects.add(new_aspect) for new_aspect in new_aspects]
#print set_aspects