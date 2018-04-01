from opinion_aspect_extraction import *
import pandas as pd
import numpy as np
import sys
from nltk.stem.wordnet import WordNetLemmatizer

INPUT_FILE = sys.argv[1]
REVIEW_COLUMN_NAME = sys.argv[2]
ASPECT_COLUMN_NAME = sys.argv[3]
OPINION_COLUMN_NAME = sys.argv[4]
INDEX_COLUMN_NAME = sys.argv[5]
try:
    OUTPUT_FILE = sys.argv[6]
except:
    OUTPUT_FILE = INPUT_FILE+'_clean'

opinions = pd.read_csv(INPUT_FILE+'.csv')
#Convert aspect verbs to nouns
#opinions[ASPECT_COLUMN_NAME+'_2'] = opinions[ASPECT_COLUMN_NAME].apply(lambda word: get_derived_word(word, 'v', 'n'))
#Convert opinions verbs to nouns
#opinions[OPINION_COLUMN_NAME+'_2'] = opinions[OPINION_COLUMN_NAME].apply(lambda word: get_derived_word(word, 'v', 's'))

def find_lemma_opinion(word):
    if 'not ' in word:
        word = word.replace('not ', '')
        word = WordNetLemmatizer().lemmatize(word,'s')
        word = 'not ' + word
    else:
        word = WordNetLemmatizer().lemmatize(word,'s')
    return word.lower()        

def find_lemma_aspect(word):
    word = WordNetLemmatizer().lemmatize(word,'n')
    return word.lower()

def find_stem_opinion(word):
    if 'not ' in word:
        word = word.replace('not ', '')
        word = find_stem_word(word)
        word = 'not ' + word
    else:
        word = find_stem_word(word)
    return word.lower()



opinions = opinions[~opinions[ASPECT_COLUMN_NAME].str.contains('[^a-zA-Z\-]', regex = True)] #Take the aspects that do not have punctuation (this is usually a parsing error)
opinions = opinions[~opinions[OPINION_COLUMN_NAME].str.contains('[^a-zA-Z\-]', regex = True)] #Take the aspects that do not have punctuation (this is usually a parsing error)
opinions[ASPECT_COLUMN_NAME+'_LEMMA'] = opinions[ASPECT_COLUMN_NAME].apply(find_lemma_aspect)
opinions[OPINION_COLUMN_NAME+'_LEMMA'] = opinions[OPINION_COLUMN_NAME].apply(find_lemma_opinion)
opinions[ASPECT_COLUMN_NAME+'_STEM'] = opinions[ASPECT_COLUMN_NAME].apply(find_stem_word)
opinions[OPINION_COLUMN_NAME+'_STEM'] = opinions[OPINION_COLUMN_NAME].apply(find_stem_opinion)
#opinions = opinions[np.isfinite(opinions[[ASPECT_COLUMN_NAME+'_STEM', OPINION_COLUMN_NAME+'_STEM']])]
opinions = opinions.dropna(subset = [ASPECT_COLUMN_NAME+'_LEMMA'])
opinions = opinions.dropna(subset = [OPINION_COLUMN_NAME+'_LEMMA'])
opinions = opinions.dropna(subset = [ASPECT_COLUMN_NAME+'_STEM'])
opinions = opinions.dropna(subset = [OPINION_COLUMN_NAME+'_STEM'])
#Drop duplicates based on review, aspect, opinion and index
print 'Before dropping duplicates: ', len(opinions)
opinions = opinions.drop_duplicates(subset = [INDEX_COLUMN_NAME, REVIEW_COLUMN_NAME, ASPECT_COLUMN_NAME, OPINION_COLUMN_NAME])
print 'After dropping duplicates: ', len(opinions)
opinions.to_csv(OUTPUT_FILE+'.csv', index = False)