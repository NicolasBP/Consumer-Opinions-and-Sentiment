from nltk.corpus import wordnet as wn

def get_derived_word(the_word, word_type, target_type):
    the_synsets = wn.synsets(the_word, pos=word_type)
    #print noun_synsets
    if not the_synsets:
        return []

    # Get all verb lemmas of the word
    the_lemmas = [l for s in the_synsets for l in s.lemmas() if s.name().split('.')[1] == word_type]
    
    derivationally_related_forms = [(l, l.derivationally_related_forms()) for l in the_lemmas]
    
    related_target_type_lemmas = [l for drf in derivationally_related_forms for l in drf[1] if l.synset().name().split('.')[1] == target_type]
    words = [l.name() for l in related_target_type_lemmas]
    len_words = len(words)
    
    # Build the result in the form of a list containing tuples (word, probability)
    result = [(w, float(words.count(w))/len_words) for w in set(words)]
    result.sort(key=lambda w: -w[1])

    # return all the possibilities sorted by probability
    return result[0][0]


#print get_derived_word('dizzy', 'n', 's')
#print get_derived_word('seem', 'v', 's')