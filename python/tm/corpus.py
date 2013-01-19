'''
TME_HOME=/home/birksworks/Projects/TME
export PYTHONPATH=$TME_HOME/tme/python:$PYTHONPATH
source $TME_HOME/venv/bin/activate
cd $TME_HOME/tme/python
ipython
from gensim import corpora, models, similarities
from random import choice
from tm import corpus
HOME_DIRECTORY = '/home/birksworks/Projects/TME'
data = corpus.build_corpus()
d, m = corpus.model_corpus(no_below=4, no_above=0.5, keep_n=1000, num_topics=120)
c = [d.doc2bow(item['text']) for item in data.values()]
i = similarities.MatrixSimilarity(m[c])
def similars(data=data, m=m, i=i, index=None, n=20):
    if index:
        item = data.values()[index]
    else:
        item = choice(data.values())
    print '-->', item['id']
    doc = item['text']
    bow = d.doc2bow(doc)
    lda = m[bow]
    sims = sorted(enumerate(i[lda] ), key=lambda item: -item[1])
    for pos in range(n): 
        ii, score = sims[pos]
        print ii, data.values()[ii]['id'], score
    
similars()


m = corpus.ngram_model(data)
t = model.state.get_lambda()[0]
corpus.best_keyphrases(labels, t, m, d)


doc = data['ml-3627']['text']
doc = data['tr-1922']['text']
bow = d.doc2bow(doc)
lda = m[bow]
print lda

c = [d.doc2bow(item['text']) for item in data.values()]
mc = m[c]
cnt = 0
t_map = {}
for v in mc:
    t_map[data.values()[cnt]['id']] = v
    cnt += 1
    
i = similarities.MatrixSimilarity(m[c])
i = similarities.SparseMatrixSimilarity(m[c])
sims = i[lda] 
sims = sorted(enumerate(sims), key=lambda item: -item[1])
def similars(data=data, m=m, i=i, index=None, n=20):
    if index:
        item = data.values()[index]
    else:
        item = choice(data.values())
    print '-->', item['id']
    doc = item['text']
    bow = d.doc2bow(doc)
    lda = m[bow]
    sims = sorted(enumerate(i[lda] ), key=lambda item: -item[1])
    for pos in range(n): 
        ii, score = sims[pos]
        print ii, data.values()[ii]['id'], score
    

def similars(index=None, n=20):
    if index:
        item = data.values()[index]
    else:
        item = choice(data.values())
    print '-->', item['id']
    lda = t_map[item['id']]
    sims = sorted(enumerate(i[lda] ), key=lambda item: -item[1])
    for pos in range(n): 
        ii, score = sims[pos]
        print ii, data.values()[ii]['id'], score


'''
from data.util import word_tokenize_doc
from nltk.corpus import stopwords as nltk_stopwords 
import os
import simplejson
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=DeprecationWarning)
    from gensim import corpora, models, similarities
    from gensim.utils import tokenize

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
            #text = list(tokenize(content.lower()))
            #text = content.lower().split()
            text = word_tokenize_doc(content.lower())
            data[project_id] = {
                'id':project_id,
                'title':title[0],
                'text':text,
                'content':content,
            }
    return data

def build_dictionary(data, no_below=4, no_above=0.5, keep_n=2500):
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

def build_bow_corpus(data, dictionary):
    '''
    Builds a bag-of-words corpus from documents in the given directory 
    and returns the document data, dictionary and corpus.
    ''' 
    texts = [item['text'] for item in data.values()]
    bow_corpus = [dictionary.doc2bow(text) for text in texts]
    return bow_corpus

def build_and_save_dictionary(data, directory=HOME_DIRECTORY, no_below=4, no_above=0.5, keep_n=2500):
    '''
    Builds and saves a gensim dictionary based on the given corpus.
        @param no_below: A lower limit on the number of documents a token must appear in to be kept.
        @param no_above: An upper limit on the proportions of documents a token can appear in to be kept.
        @param keep_n: The number of most frequent tokens to keep.
    ''' 
    texts = [[token for token in doc['text'] if len(token) > 1] for doc in data.values()]
    dictionary = corpora.Dictionary(texts)
    stopword_ids = [dictionary.token2id[word] for word in stop_words(directory) 
        if word in dictionary.token2id]
    dictionary.filter_tokens(bad_ids=stopword_ids)
    dictionary.filter_extremes(no_below=no_below, no_above=no_above, keep_n=keep_n)
    dictionary.compactify()
    dictionary.save("%s/model/tm.dict" % directory)
    return dictionary

def build_and_save_lda_model(dictionary, bow_corpus, directory=HOME_DIRECTORY, num_topics=12):
    '''
    Builds and saves an LDA model based on the given dictioinary and corpus.
        @param num_topics: The number of topics to use in building the LDA model.
    ''' 
    lda = models.ldamodel.LdaModel(bow_corpus, id2word=dictionary, num_topics=num_topics)
    lda.save('%s/model/tm.lda' % directory)
    return lda
    
def model_corpus(directory=HOME_DIRECTORY, num_topics=12, no_below=4, no_above=0.5, keep_n=2500):
    data = build_corpus(directory)
    dictionary = build_and_save_dictionary(
        data, 
        directory, 
        no_below=no_below, 
        no_above=no_above, 
        keep_n=keep_n
    )
    bow_corpus = get_bow_corpus(data, dictionary)
    model = build_and_save_lda_model(dictionary, bow_corpus, directory, num_topics=num_topics)
    for t in model.show_topics(topics=num_topics): print t
    return dictionary, model
from math import log
from nltk.model import NgramModel  
from nltk.probability import LidstoneProbDist, WittenBellProbDist
def ngram_model(data, n=1, text=None):
    if not text: text = sum([item['text'] for item in data.values()], [])
    estimator = lambda fdist, bins: LidstoneProbDist(fdist, 0.2)
    model = NgramModel(n, text, estimator=estimator)
    return model

def zl_score(l, t, m, d):
    score = 0
    t = t / sum(t)
    for w in l.split(): 
        if w in d.token2id:
            p = m.prob(w, [])
            pt = t[d.token2id[w]]
            score += log(pt/p)
    return score
        
def best_keyphrase(labels, t, m, d):
    best_score = -float('inf')
    best_kp = None
    for l in labels:   
        score = zl_score(l, t, m, d)
        if score >= best_score:
            best_score = score
            best_kp = l
    return best_kp, best_score
        
def best_keyphrases(labels, t, m, d):
    return sorted([(l, zl_score(l, t, m, d)) for l in labels], key=lambda item: -item[1])[:4]
    
#model = models.ldamodel.LdaModel.load('%s/model/tm.lda' % directory)
