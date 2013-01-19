'''
This module provides support for building topic models for the Truonex
project corpus.

from tm import modeler
data, dictionary, model = modeler.build_lda_topic_model(no_below=10, no_above=0.25, keep_n=1000, num_topics=24)
'''
from data.util import word_tokenize_doc
from gensim import corpora, models, similarities
from nltk.corpus import stopwords as nltk_stopwords 
import os
import simplejson
    
HOME_DIRECTORY = '/home/birksworks/Projects/TME'

def stop_words(directory=HOME_DIRECTORY):
    stopwords = nltk_stopwords.words('english')
    f = open('%s/model/stop-words.lst' % directory)
    stopwords.extend(f.read().split())
    f.close()
    return stopwords

def build_corpus(directory=HOME_DIRECTORY):
    '''
    Builds and returns a corpus based on the text documents in the given directory.
    ''' 
    f = open('%s/tme-corpus/title-map.json' % directory)
    title_map = simplejson.load(f) 
    f.close()
    data = {}
    file_list = os.listdir('%s/tme-corpus' % directory)
    for file_name in file_list:
        if file_name.endswith('txt'): 
            project_id = file_name[:-4]            
            title=title_map[project_id],
            content = open(directory+"/tme-corpus/"+file_name).read()
            text = word_tokenize_doc(content.lower())
            data[project_id] = {
                'id':project_id,
                'title':title[0],
                'text':text,
                'content':content,
            }
    return data

def build_dictionary(directory, data, no_below=4, no_above=0.5, keep_n=2500):
    '''
    Builds and returns a gensim dictionary based on the given data and parameters.
        @param no_below: A lower limit on the number of documents a token must appear in to be kept.
        @param no_above: An upper limit on the proportions of documents a token can appear in to be kept.
        @param keep_n: The number of most frequent tokens to keep.
    ''' 
    texts = [[token for token in doc['text'] if len(token) > 1] for doc in data.values()]
    dictionary = corpora.Dictionary(texts)
    stopword_ids = [dictionary.token2id[word] for word in stop_words(directory) if word in dictionary.token2id]
    dictionary.filter_tokens(bad_ids=stopword_ids)
    dictionary.filter_extremes(no_below=no_below, no_above=no_above, keep_n=keep_n)
    dictionary.compactify()
    return dictionary

def get_truonex_data(data):
    '''
    Extracts and returns Truonex project data from the given data map.
    ''' 
    return dict((k, v) for k, v in data.iteritems() if k.startswith('tr-'))

def build_bow_corpus(data, dictionary):
    '''
    Builds a bag-of-words corpus from documents in the given directory 
    and returns the document data, dictionary and corpus.
    ''' 
    texts = [item['text'] for item in data.values()]
    bow_corpus = [dictionary.doc2bow(text) for text in texts]
    return bow_corpus

def build_lda_topic_model(directory=HOME_DIRECTORY, no_below=10, no_above=0.25, keep_n=1000, num_topics=24):
    data = build_corpus(directory)
    dictionary = build_dictionary(
        directory,
        data, 
        no_below=no_below, 
        no_above=no_above, 
        keep_n=keep_n
    )
    bow_corpus = build_bow_corpus(data, dictionary)
    model = models.ldamodel.LdaModel(bow_corpus, id2word=dictionary, num_topics=num_topics)
    return data, dictionary, model
