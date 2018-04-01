from __future__ import division  # Python 2 users only
from derived_word_forms import *
import nltk
from nltk import sent_tokenize
from nltk import word_tokenize
from nltk.stem.porter import PorterStemmer

from nltk.parse.stanford import StanfordDependencyParser
path_to_jar = 'stanford-corenlp-full-2015-12-09/stanford-corenlp-3.6.0.jar'
path_to_models_jar = 'stanford-corenlp-full-2015-12-09/stanford-corenlp-3.6.0-models.jar'
dependency_parser = StanfordDependencyParser(path_to_jar=path_to_jar, path_to_models_jar=path_to_models_jar)

def get_dependencies(sentence):
    dependency_parser = StanfordDependencyParser(path_to_jar=path_to_jar, path_to_models_jar=path_to_models_jar)
    result = dependency_parser.raw_parse(sentence)
    dep = result.next()
    return list(dep.triples())

def R11_R21(relation, sentence, word, provided_term_types, extract_term_types):
    extraction_terms = set()
    extraction_dependencies = set()
    try:
        dependencies = get_dependencies(sentence)
        #Extract opinion from aspect
        #[extraction_terms.add(value1) for (value1, value2, value3) in dependencies if value2 in relation and find_stem_word(value3[0]) == find_stem_word(word) and value3[1] in provided_term_types and value1[1] in extract_term_types]
        [extraction_dependencies.add(dependency) for dependency in dependencies if dependency[1] in relation and find_stem_word(dependency[2][0]) == find_stem_word(word) and dependency[2][1] in provided_term_types and dependency[0][1] in extract_term_types]
        ##print 'extraction_dependencies', extraction_dependencies
        if extraction_dependencies:
            for extraction_dependency in list(extraction_dependencies):
                negated = False
                ##print 'extraction_dependency', extraction_dependency
                negated = any([dependency[1]=='neg' and extraction_dependency[0][0] == dependency[0][0] for dependency in dependencies])
                if negated:
                    #[extraction_terms.add('not' + dependency[0][0]) for dependency in dependencies if dependency[1]=='neg' and extraction_dependency[0][0] == dependency[0][0]]
                    extraction_terms.add('not ' + extraction_dependency[0][0])
                else:
                    extraction_terms.add(extraction_dependency[0][0])
        if extraction_terms:
            return list(extraction_terms)
        #Extract aspect from opinion, or opinion from verb phrase (does not account for negation)
        [extraction_terms.add(value3[0]) for (value1, value2, value3) in dependencies if value2 in relation and find_stem_word(value1[0]) == find_stem_word(word) and value1[1] in provided_term_types and value3[1] in extract_term_types]
        ##print 'extraction_terms', extraction_terms
        #[extraction_dependencies.add(dependency) for dependency in dependencies if dependency[1] in relation and find_stem_word(dependency[0][0]) == find_stem_word(word) and dependency[0][1] in provided_term_types and dependency[2][1] in extract_term_types]   
        #if extraction_terms:
    except AssertionError:
        print 'AssertionError on sentence', sentence, ' ...Skipping sentence...'
        return list(extraction_terms)
    except ValueError:
        print 'ValueError on sentence', sentence, ' .... Skipping sentence...'
        return list(extraction_terms)
    except:
        print 'Unexpected Error on sentence', sentence, ' ...Skipping sentence...'
        return list(extraction_terms)
    return list(extraction_terms)

def R12_R22(relation1, relation2, sentence, word, provided_term_types, extract_term_types):
    extraction_terms = set()
    try:
        dependencies = get_dependencies(sentence)
        h = [value1 for (value1, value2, value3) in dependencies if value2 in relation1 and find_stem_word(value3[0]) == find_stem_word(word) and value3[1] in provided_term_types]
        for h_term in h:
           	negated = False
           	negated = any([dependency[1]=='neg' and dependency[0] == h_term for dependency in dependencies])
           	if negated:
           	    [extraction_terms.add('not ' + value3[0]) for (value1, value2, value3) in dependencies if value2 in relation2 and value1==h_term and value3[1] in extract_term_types]
           	else:
           	    [extraction_terms.add(value3[0]) for (value1, value2, value3) in dependencies if value2 in relation2 and value1==h_term and value3[1] in extract_term_types]
        #[extraction_terms.add(value3) for (value1, value2, value3) in dependencies if value2 in relation2 and value1 in h and value3[1] in extract_term_types]
    except AssertionError:
        print 'AssertionError on sentence', sentence, ' ...Skipping sentence...'
        return list(extraction_terms)
    except ValueError:
        print 'ValueError on sentence', sentence, ' .... Skipping sentence...'
        return list(extraction_terms)
    except:
        print 'Unexpected Error on sentence', sentence, ' ...Skipping sentence...'
        return list(extraction_terms)
    return list(extraction_terms)

def R31_R41(relation, sentence, word, extract_term_types):
    extraction_term = set()
    try:
        dependencies = get_dependencies(sentence)
        print 'Extracting terms from sentence: ', sentence
        [extraction_term.add(find_if_direcly_negated(dependencies, value3[0])) for (value1, value2, value3) in dependencies if value2 in relation and value1[0] == word and value3[1] in extract_term_types]
        #Look for terms to extract in the other direction of the relationship.
        [extraction_term.add(find_if_direcly_negated(dependencies, value1[0])) for (value1, value2, value3) in dependencies if value2 in relation and value3[0] == word and value1[1] in extract_term_types]
        #aspects = [[aspect for aspect in aspects if aspect != []][0]]
    except AssertionError:
        print 'AssertionError on sentence', sentence, ' ...Skipping sentence...'
        return list(extraction_term)
    except ValueError:
        print 'ValueError on sentence', sentence, ' .... Skipping sentence...'
        return list(extraction_term)
    except:
        print 'Unexpected Error on sentence', sentence, ' ...Skipping sentence...'
        return list(extraction_term)
    return list(extraction_term)

def find_if_direcly_negated(dependencies, opinion_word):
    negated = False
    result = opinion_word
    negated = any([dependency[1]=='neg' and find_stem_word(dependency[0][0]) == find_stem_word(opinion_word) for dependency in dependencies])
    if negated:
        result = 'not ' + opinion_word
    return result
    
#def find_opinions_from_opinions(sentence, opinions):
#    opinions_from_opinions = set()
#    temp_opinions = set(opinions)
#    if opinions:
#        for opinion in opinions:
#            base_opinion = opinion
#            if 'not ' in opinion:
#                base_opinion = base_opinion.replace('not ', '')
#            new_opinions = (R31_R41(CONJ, sentence, base_opinion, ['JJ', 'JJS', 'JJR']))
#            if not set(new_opinions).issubset(opinions):
#                [opinions_from_opinions.add(new_opinion) for new_opinion in new_opinions if new_opinions]
#                [temp_opinions.add(opinions_from_opinion) for opinions_from_opinion in opinions_from_opinions if opinions_from_opinions]
#                print 'case7: ', temp_opinions
#                temp_opinions = find_opinions_from_opinions(sentence, temp_opinions)
#    return temp_opinions
    
def find_opinions_from_opinions(sentence, opinions, last_new_opinions = None):
    opinions_from_opinions = set()
    new_opinions = set()
    if last_new_opinions:
        iter_opinions = last_new_opinions
    else:
        iter_opinions = opinions
    temp_opinions = set(opinions)
    if iter_opinions:
        for opinion in iter_opinions:
            print 'Based on opinion: ', opinion
            base_opinion = opinion
            if 'not ' in opinion:
                base_opinion = base_opinion.replace('not ', '')
            print 'Analyzing rule R31_R41...'
            [new_opinions.add(new_opinion) for new_opinion in R31_R41(CONJ, sentence, base_opinion, ['JJ', 'JJS', 'JJR'])]
            #print 'case7: ', new_opinions
            if last_new_opinions:
                print 'adding last new opinions (', last_new_opinions, ') to current list...'
                temp_opinions = temp_opinions.union(last_new_opinions)
            if not new_opinions.issubset(temp_opinions):
                print 'new opinions: ', new_opinions
                [opinions_from_opinions.add(new_opinion) for new_opinion in new_opinions if new_opinions]
                #[temp_opinions.add(opinions_from_opinion) for opinions_from_opinion in opinions_from_opinions if opinions_from_opinions]
                #print 'case7: ', new_opinions
                print 'calling find_opinions_from_opinions with new opinions: ', opinions_from_opinions
                temp_opinions = find_opinions_from_opinions(sentence, temp_opinions, opinions_from_opinions)
                #return temp_opinions
    #print 'case7: ', temp_opinions
    return temp_opinions

def R32_R42(relation1, relation2, sentence, word, extract_term_types):
    aspects = set()
    try:
        dependencies = get_dependencies(sentence)
        print 'Extracting terms from sentence: ', sentence
        #Extract all h words that are related to the provided word
        h = [(value1, value2, value3) for (value1, value2, value3) in dependencies if value3[0] == word]
        #print 'h:', h
        #For each h word
        for each_h in h:
            #For each dependency related to each_h
            #print 'each_h: ',each_h
            each_h_dependency = [(value1, value2, value3) for (value1, value2, value3) in dependencies if value1[0] == each_h[0][0]]
            #print 'each_h_dependency: ', each_h_dependency
            #Compare the current dependency to each one of the remaining dependencies
            for current_dependency in each_h_dependency:
                #Append it to the output...
                #If the current dependency is not the same as the other dependency
                #and the current dependency's relationship is the same as another dependency's relationship
                #and if that dependency is in ['NN', 'NNP']
                [aspects.add(value3[0]) for (value1, value2, value3) in each_h_dependency if (current_dependency[2][0] != value3[0] and value3[0] != word and current_dependency[1] == value2 and value3[1] in extract_term_types)]
                #Append to output...
                #If the current dependency's relationship is in relation1 and another dependency's relationship is in relation2 
                #and if that dependency is in ['NN', 'NNP']
                #aspects.append([value3 for (value1, value2, value3) in each_h_dependency if(current_dependency[2][0] != value3[0] and value3[0] != word and current_dependency[1] in relation1 and value2 in relation2 and value3[1] in extract_term_types)])
                [aspects.add(value3[0]) for (value1, value2, value3) in each_h_dependency if(current_dependency[2][0] != value3[0] and value3[0] != word and current_dependency[1] in relation1 and value2 in relation2 and value3[1] in extract_term_types)]
                #aspects = filter(None, aspects)
        #print aspects
        #aspects = [[aspect for aspect in aspects if aspect != []][0]]
    except AssertionError:
        print 'AssertionError on sentence', sentence, ' ...Skipping sentence...'
        return list(aspects)
    except ValueError:
        print 'ValueError on sentence', sentence, ' .... Skipping sentence...'
        return list(aspects)
    except:
        print 'Unexpected Error on sentence', sentence, ' ...Skipping sentence...'
        return list(aspects)
    return list(aspects)

#Use for: extract_term_types -> relation2 -> word1(provided_term_types 1)
#Provided that:word1 -> relation1 -> provided_term_types2
def R51(relation1, relation2, sentence, word1, provided_term_types1, provided_term_types2, extract_term_types):
    extraction_terms = set()
    extraction_terms_result = set()
    try:
        dependencies = get_dependencies(sentence)
        [extraction_terms.add(value1) for (value1, value2, value3) in dependencies if value2 in relation1 and find_stem_word(value1[0]) == find_stem_word(word1) and value1[1] in provided_term_types1 and value3[1] in provided_term_types2]
        for extraction_term, extraction_term_type in list(extraction_terms):
            [extraction_terms_result.add(value1[0]) for (value1, value2, value3) in dependencies if value2 in relation2 and find_stem_word(value3[0]) == find_stem_word(extraction_term) and find_stem_word(value3[1]) == find_stem_word(extraction_term_type)]
    except AssertionError:
        print 'AssertionError on sentence', sentence, ' ...Skipping sentence...'
        return list(extraction_terms)
    except ValueError:
        print 'ValueError on sentence', sentence, ' .... Skipping sentence...'
        return list(extraction_terms)
    except:
        print 'Unexpected Error on sentence', sentence, ' ...Skipping sentence...'
        return list(extraction_terms)
    return list(extraction_terms_result)

#sentence is the sentence to be analyzed
#word for which opinion is to be extracted
#word_types is ['VB', 'VBZ', 'VBP']
#relations is ['ccomp', 'xcomp']
#extracted_term_types is ['JJ']
def R61(sentence, word, word_types, relations, extracted_term_types, extract_verb_children):
    result = []
    try:
        negated_terms = set()
        dependencies = get_dependencies(sentence)
        [negated_terms.add(value1[0]) for (value1, value2, value3) in dependencies if value2=='neg' and value1[1] in word_types]
        negated_terms = list(negated_terms)
        ##print 'negated_terms: ', negated_terms
        #check_for_children = True
        for negated_term in negated_terms:
            if extract_verb_children:
                result = extract_verb_comps_children(dependencies, word_types, word, relations, extracted_term_types, negated_term)
            else:
                result = extract_noun_comps_children(dependencies, word_types, word, relations, extracted_term_types, negated_term)
            if result:
                return result
    except AssertionError:
        print 'AssertionError on sentence', sentence, ' ...Skipping sentence...'
        return list(result)
    except ValueError:
        print 'ValueError on sentence', sentence, ' .... Skipping sentence...'
        return list(result)
    except:
        print 'Unexpected Error on sentence', sentence, ' ...Skipping sentence...'
        return list(result)
    
            #parents = [negated_term]
            #print parents
            #while check_for_children:
            #    parents = new_parents
            #    for parent in parents:
            #        comps_dependencies = set()
            #        #Look for any terms that are related to the parent through ccomp or xcomp relationship
            #        [comps_dependencies.add(dependency) for dependency in dependencies if dependency[1] in relations and dependency[0][0] == parent and dependency[0][1] in word_types]
            #        print list(comps_dependencies)
            #        if not comps_dependencies:
            #            continue
            #        else:
            #            #extracted_term_types2 is ['JJ']
            #            result = set()
            #            [result.append(dependency[2][0]) for dependency in list(comps_dependencies) if find_stem_word(dependency[0][0]) == find_stem_word(word) and dependency[1] in relations and dependency[2][1] in extracted_term_types]
            #            print list(result)
            #            if result:
            #                return list(result)
            #            else:
            #                new_parents = [comps_dependency[2][0] for comps_dependency in comps_dependencies]
            #                print parents
                        
def extract_verb_comps_children(dependencies, word_types, word, relations, extracted_term_types, parent):
    comps_dependencies = set()
    #Look for any terms that are related to the parent through ccomp or xcomp relationship
    [comps_dependencies.add(dependency) for dependency in dependencies if dependency[1] in relations and dependency[0][0] == parent and dependency[0][1] in word_types]
    print 'comps_dependencies: ', list(comps_dependencies)
    if not comps_dependencies:
        return list(comps_dependencies)
    else:
        #extracted_term_types2 is ['JJ']
        result = set()
        [result.add('not ' + dependency[2][0]) for dependency in list(comps_dependencies) if find_stem_word(dependency[0][0]) == find_stem_word(word) and dependency[1] in relations and dependency[2][1] in extracted_term_types]
        print 'results list: ', list(result)
        if result:
            return list(result)
        else:
            new_parents = [comps_dependency[2][0] for comps_dependency in comps_dependencies]
            for new_parent in new_parents:
                print 'new parent: ', new_parent
                results = extract_verb_comps_children(dependencies, word_types, word, relations, extracted_term_types, new_parent)
                if results:
                    return list(results)

def extract_noun_comps_children(dependencies, word_types, word, relations, extracted_term_types, parent):
    comps_dependencies = set()
    #Look for any terms that are related to the parent through ccomp or xcomp relationship
    [comps_dependencies.add(dependency) for dependency in dependencies if dependency[1] in relations and dependency[0][0] == parent and dependency[0][1] in word_types]
    print 'comps_dependencies: ', list(comps_dependencies)
    if not comps_dependencies:
        return list(comps_dependencies)
    else:
        #extracted_term_types2 is ['JJ']
        result = set()
        for comps_dependency in comps_dependencies:
            #[result.add('not ' + value1[0]) for (value1,value2,value3) in dependencies if value1[0] == comps_dependency[2][0] and value2 in MR and value1[1] in extracted_term_types and find_stem_word(value3[0]) == find_stem_word(word)]
            [result.add('not ' + value3[0]) for (value1,value2,value3) in dependencies if value1[0] == comps_dependency[2][0] and value2 in MR and value3[1] in extracted_term_types and find_stem_word(value1[0]) == find_stem_word(word)]
        print 'results list: ', list(result)
        if result:
            return list(result)
        else:
            new_parents = [comps_dependency[2][0] for comps_dependency in comps_dependencies]
            for new_parent in new_parents:
                print 'new parent: ', new_parent
                results = extract_noun_comps_children(dependencies, word_types, word, relations, extracted_term_types, new_parent)
                if results:
                    return list(results)

def find_if_opinion_negated(sentence, aspect, opinion, dependencies):
    negated = False
    #negated = any(True for dependency in dependencies if dependency[1]=='neg' and find_stem_word(dependency[0][0]) == find_stem_word(opinion))
    #the opinion is negated if there is a negation relationship directly tied to the opinion word: The taste is not good
    negated = any([dependency[1]=='neg' and find_stem_word(dependency[0][0]) == find_stem_word(opinion) for dependency in dependencies])
    #the opinion is negated if a verb affecting the noun is in turn affected by a negation (ie. It doesn't taste good)
    verbs_affecting_noun = set([value1[0] for (value1, value2,value3) in dependencies if value2 in MR and find_stem_word(value3[0]) == find_stem_word(aspect) and value1[1] in ['VB','VBP','VBZ']])
    for verb_affecting_noun in list(verbs_affecting_noun):
        negated = any([dependency[1]=='neg' and dependency[0][0] == verb_affecting_noun for dependency in dependencies])
        if negated:
            return True
    #Need to model case: the opinion is negated if a verb affecting the noun is affected directly by (or is an auxiliarive of) any other verb that is being negated. (Ex: I don't think it makes me feel good)
    #Need to model case: the opinion is dependent on the verb and the verb is being negated (Ex: It doesn't feel good)
    
    

        
    
    
    return negated


MR = ['amod', 'nmod', 'nsubj', 'dobj', 'iobj']
CONJ = ['conj', 'dep']
SUBJ = ['nsubj']
DOBJ = ['dobj']
MOD = ['amod', 'nmod']
NN = ['NN']
XCOMP = ['xcomp']
MARK = ['mark']

def find_stem_word(word):
    try:
        stemmer = PorterStemmer()
        stem_word = stemmer.stem(word)
    except ValueError:
        stem_word = word
    return stem_word

#not used
def add_opinion_to_set(sentence, aspect, opinion):
    dependencies = get_dependencies(sentence)
    if find_if_opinion_negated(sentence, aspect, opinion, dependencies):
        return 'not ' + opinion
    return opinion

def determine_if_sentence_has_opinion(sentence, opinion_type, aspect_type):
    has_opinion = False
    has_aspect = False
    try:
        dependencies = get_dependencies(sentence)
        has_opinion = any([dependency[0][1] in opinion_type or dependency[2][1] in opinion_type for dependency in dependencies])
        has_aspect = any([dependency[0][1] in aspect_type or dependency[2][1] in aspect_type for dependency in dependencies])
    except AssertionError:
        print 'AssertionError on sentence', sentence, ' ...Skipping sentence...'
        return False
    except ValueError:
        print 'ValueError on sentence', sentence, ' .... Skipping sentence...'
        return False
    except:
        print 'Unexpected Error on sentence', sentence, ' ...Skipping sentence...'
        return False
    return (has_opinion and has_aspect)

def extract_aspects_from_aspects(sentence, aspects, last_new_aspects = None):
    aspects_from_aspects = set()
    new_aspects = set()
    if last_new_aspects:
        iter_aspects = last_new_aspects
    else:
        iter_aspects = aspects
    temp_aspects = set(aspects)
    if iter_aspects:
        for aspect in iter_aspects:
            print 'Based on aspect: ', aspect
            print 'Analyzing rule R31_R41...'
            #new_aspects = set(R31_R41(CONJ, sentence, aspect, ['NN', 'NNP', 'NNS']))
            [new_aspects.add(new_aspect) for new_aspect in R31_R41(CONJ, sentence, aspect, ['NN', 'NNP', 'NNS'])]
            #print 'new aspects: ', new_aspects
            print 'Analyzing rule R32_R42...'
            [new_aspects.add(new_aspect) for new_aspect in R32_R42(SUBJ, DOBJ, sentence, aspect, ['NN', 'NNP', 'NNS'])]
            print 'total new aspects: ', new_aspects
        if last_new_aspects:
            print 'adding last new aspects (', last_new_aspects, ') to current list...'
            #last_new_aspects = {find_stem_word(last_new_aspect) for last_new_aspect in last_new_aspects}
            temp_aspects = temp_aspects.union(last_new_aspects)
        #new_aspects_stem = {find_stem_word(new_aspect) for new_aspect in new_aspects}
        #temp_aspects_stem = {find_stem_word(temp_aspect) for temp_aspect in temp_aspects}
        if not new_aspects.issubset(temp_aspects):
            print 'adding new aspects to list...'
            [aspects_from_aspects.add(new_aspect) for new_aspect in new_aspects if new_aspects]
            #[temp_aspects.add(aspects_from_aspect) for aspects_from_aspect in aspects_from_aspects if aspects_from_aspects]
            temp_aspects = extract_aspects_from_aspects(sentence, temp_aspects, aspects_from_aspects)
    print 'All aspects from this sentence: ', temp_aspects
    return temp_aspects




#def resolve_conflicting_opinions(opinions):
#    result = list(opinions)
#    for opinion in opinions:
#        if 'not ' in opinion:
#            positive_opinion = str(opinion).replace('not ', '')
#            if positive_opinion in opinions:
#                print 'Resolving conflicting opinions...'
#                result.remove(positive_opinion)
#    return result

def resolve_conflicting_opinions(aspect_opinions):
    print 'Resolving conflicting opinions...'
    negatives_to_positives = {(aspect,str(opinion).replace('not ', '')) for (aspect,opinion) in aspect_opinions if 'not ' in opinion}
    aspect_opinions = aspect_opinions.difference(negatives_to_positives)
    return aspect_opinions
       

def extract_opinion(sentence, aspect):
    has_aspect_opinion = determine_if_sentence_has_opinion(sentence, ['JJ', 'JJS', 'JJR'], ['NN', 'NNP', 'NNS', 'VB','VBP','VBZ'])
    if has_aspect_opinion:
        print '\n##Analyzing sentence: ', sentence
        opinions = set()
        aspect_opinions = set()
        nounified_aspect = None
        case1 = R11_R21(MR, sentence, aspect, ['NN', 'NNP', 'NNS'], ['JJ', 'JJS', 'JJR'])
        case2 = R12_R22(MR, MR, sentence, aspect, ['NN', 'NNP', 'NNS'], ['JJ', 'JJS', 'JJR'])
        case3 = R11_R21(XCOMP, sentence, aspect, ['VB','VBP','VBZ'], ['JJ', 'JJS', 'JJR'])
        case4 = R51(MARK, XCOMP, sentence, aspect, ['VB','VBP','VBZ'], ['TO'], ['JJ', 'JJS', 'JJR'])
        #negatives
        case5 = R61(sentence, aspect, ['VB', 'VBZ', 'VBP'], ['ccomp', 'xcomp', 'acomp', 'advcl', 'dobj'], ['JJ'], False)
        case6 = R61(sentence, aspect, ['VB', 'VBZ', 'VBP'], ['ccomp', 'xcomp', 'acomp', 'advcl', 'dobj'], ['JJ'], True)
        #case5 = R61(sentence, aspect, ['VB', 'VBZ', 'VBP'], ['ccomp', 'xcomp', 'advcl'], ['JJ'], True)
        #[opinions.add(add_opinion_to_set(sentence, aspect, opinion[0])) for opinion in R11_R21(MR, sentence, aspect, ['NN', 'NNP'], ['JJ', 'JJS', 'JJR'])]  #extract_opinion('the shake has good taste', 'taste') -> good
        if case1:
            [opinions.add(opinion) for opinion in case1]  #extract_opinion('the shake has good taste', 'taste') -> good
            #aspect_opinions.add(set(zip([aspect]*len(opinions), opinions)))
            [aspect_opinions.add((aspect, opinion)) for (aspect, opinion) in zip([aspect]*len(case1), case1)]
            print 'case1: ', list(aspect_opinions)
        #[opinions.add(add_opinion_to_set(sentence, aspect, opinion[0])) for opinion in R11_R21(XCOMP, sentence, aspect, ['VB','VBP','VBZ'], ['JJ', 'JJS', 'JJR'])] #extract_opinion('It makes me feel good', 'feel')-> good
        if case2:
            [opinions.add(opinion) for opinion in case2] #extract_opinion('Soylent is the best meal replacement shake', 'Soylent') ->best
            [aspect_opinions.add((aspect, opinion)) for (aspect, opinion) in zip([aspect]*len(case2), case2)]
            print 'case2: ', list(aspect_opinions)
        if case3:
            [opinions.add(opinion) for opinion in case3] #extract_opinion('It makes me feel good', 'feel')-> good
            if get_derived_word(aspect, 'v', 'n'):
                nounified_aspect = get_derived_word(aspect, 'v', 'n')
                [aspect_opinions.add((aspect, opinion)) for (aspect, opinion) in zip([nounified_aspect]*len(case3), case3)]
            else:
                [aspect_opinions.add((aspect, opinion)) for (aspect, opinion) in zip([aspect]*len(case3), case3)]
            #try:
            #    nounified_aspect = get_derived_word(aspect, 'v', 'n')
            #    [aspect_opinions.add((aspect, opinion)) for (aspect, opinion) in zip([nounified_aspect]*len(case3), case3)]
            #except TypeError:
            #    print 'case3 (TypeError): ', case3
            #    print 'aspect: ', aspect
            #    print 'opinions (TypeError)', opinions
            #    [aspect_opinions.add((aspect, opinion)) for (aspect, opinion) in zip([aspect]*len(case3), case3)]
            print 'case3: ', list(aspect_opinions)
        if case4:
            [opinions.add(opinion) for opinion in case4] #extract_opinion("It's pretty cheap to buy at Target", 'buy') -> cheap
            if get_derived_word(aspect, 'v', 'n'):
                nounified_aspect = get_derived_word(aspect, 'v', 'n')
                [aspect_opinions.add((aspect, opinion)) for (aspect, opinion) in zip([nounified_aspect]*len(case4), case4)]
            else:
                [aspect_opinions.add((aspect, opinion)) for (aspect, opinion) in zip([aspect]*len(case4), case4)]
            #nounified_aspect = get_derived_word(aspect, 'v', 'n')
            #[aspect_opinions.add((aspect, opinion)) for (aspect, opinion) in zip([nounified_aspect]*len(case4), case4)]
            print 'case4: ', list(aspect_opinions)
        #negatives
        if case5:
            [opinions.add(opinion) for opinion in case5]
            if get_derived_word(aspect, 'v', 'n'):
                nounified_aspect = get_derived_word(aspect, 'v', 'n')
                [aspect_opinions.add((aspect, opinion)) for (aspect, opinion) in zip([nounified_aspect]*len(case5), case5)]
            else:
                [aspect_opinions.add((aspect, opinion)) for (aspect, opinion) in zip([aspect]*len(case5), case5)]
            #nounified_aspect = get_derived_word(aspect, 'v', 'n')
            #[aspect_opinions.add({the_aspect, the_opinion}) for (the_aspect, the_opinion) in zip([nounified_aspect]*len(case5), case5)]
            #[aspect_opinions.add((aspect, opinion)) for (aspect, opinion) in zip([aspect]*len(case5), case5)]
            print 'case5: ', list(aspect_opinions)
        if case6:
            [opinions.add(opinion) for opinion in case6]
            if get_derived_word(aspect, 'v', 'n'):
                nounified_aspect = get_derived_word(aspect, 'v', 'n')
                [aspect_opinions.add((aspect, opinion)) for (aspect, opinion) in zip([nounified_aspect]*len(case6), case6)]
            else:
                [aspect_opinions.add((aspect, opinion)) for (aspect, opinion) in zip([aspect]*len(case6), case6)]
            #nounified_aspect = get_derived_word(aspect, 'v', 'n')
            #[aspect_opinions.add((aspect, opinion)) for (aspect, opinion) in zip([nounified_aspect]*len(case6), case6)]
            print 'case6: ', list(aspect_opinions)
        #opinions = {opinion for (aspect,opinion) in aspect_opinions}
        case7 = find_opinions_from_opinions(sentence, opinions)
        print case7
        print opinions
        if case7>opinions:
            [opinions.add(opinion) for opinion in case7]
            if nounified_aspect:
                [aspect_opinions.add((aspect, opinion)) for (aspect, opinion) in zip([nounified_aspect]*len(case7), case7)]
            else:
                [aspect_opinions.add((aspect, opinion)) for (aspect, opinion) in zip([aspect]*len(case7), case7)]
            print 'case7: ', list(aspect_opinions)
        
        return resolve_conflicting_opinions(aspect_opinions)

#print extract_opinion("The price is not fair but is not the cheapest and most inexpensive either", 'price')
#print find_opinions_from_opinions("The price is not fair but is not the cheapest and most inexpensive either", ['fair'])
#print extract_opinion("Yes its carb heavy and has ton's of sugar but this stuff works.", 'carb')
