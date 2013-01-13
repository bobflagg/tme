#!/usr/bin/python

##  Statistical NLP 2009/2010 -- Template script for HW 5
##
##  Optimise meta-parameters of n-gram language models on separate development corpus
##  http://www.cogsci.uni-osnabrueck.de/CL/teaching/09w/StatNLP/

from nltk.probability import *
from nltk.model.api import ModelI
import sys, re, random, warnings
from math import *

# define alphabet (everything else will be deleted from corpus data)
# NB: "-" has to come last so the string can be used as a regexp character range below
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'.!? -"

# wrap corpus clean-up in function so it can easily be applied to all our corpora
def cleanup (corpus):
	corpus = re.sub(r'\s+', " ", corpus)       # replace linebreaks by blanks, normalise multiple blanks
	cleanup = re.compile("[^"+ALPHABET+"]+")   # this regular expression matches one or more invalid characters
	corpus = cleanup.sub("", corpus)           # delete all invalid characters (substitute with empty string)
	return corpus

def collect_frequency_data (corpus, n_max):
    '''
        Collects and returns the frequency data necessary to estimate n-gram models up to n = n_max
        from the given training corpus.  The returned value is a list of conditional frequency distributions
            fdata = collect_frequency_data(corpus, n_max)
        where fdata[k] is a ConditionalFreqDist for k characters of history (i.e. a (k+1)-gram model).
    '''
    fdata = [ None for i in range(n_max) ] # list of n-gram models for n-1 = 0 ... n_max-1
    size = len(corpus)
    for n1 in range(n_max):
        training_pairs = [
            (corpus[i-n1:i], corpus[i])  # (history, next character) at position i in training corpus
            for i in range(n1, size)     # where i ranges from n-1 to last index in corpus (Python uses 0-based indexing!)
        ]
        fdata[n1] = ConditionalFreqDist(training_pairs) # compile data into conditional frequency distribution
    return fdata

class SimpleNgramModel(ModelI):
    '''
    A simple n-gram model with geometric smoothing controlled by a single meta-parameter 0 < q < 1.
    '''
    def __init__(self, fdata, n, q):
        self.n = n
        if (n > len(fdata)):
            raise RuntimeError("Insufficient frequency data for %d-gram model." % (n))
        self.q = q
        if (q <= 0 or q >= 1):
            raise RuntimeError("Interpolation parameter q=%f must be in range (0,1)." % (q))
        fdata = fdata[0:n] # determine conditional probabilities for required history sizes only
        self.cp = [
            ConditionalProbDist(cfd, MLEProbDist)  ## --> change this line for add-lambda smoothing
            for cfd in fdata
        ]
        # To be on the safe side, use add-one smoothing for the unigram probabilities instead of MLE
        # (the digit '7' does not occur in the romance texts of the Brown corpus, but 4 times in humour!)
        self.cp[0] = ConditionalProbDist(fdata[0], LaplaceProbDist, bins=len(ALPHABET))
    def prob(self, next_char, history):
        n1 = self.n - 1 # n1 = n - 1
        l = len(history)
        if (l < n1):
            raise RuntimeError("History '%s' too short for %d-gram model." % (history, self.n))
        while (n1 > 0 and history[(l-n1):l] not in self.cp[n1]):
            n1 -= 1 # fall back on shorter history if necessary (before interpolation / back-off !!)
        p = 0.0     # accumulate interpolated probability
        coef = 1.0  # geometric interpolation coefficient (unnormalised)
        denom = 0.0 # calculate normalising denominator by adding up unnormalised coefficients
        for k in range(n1, -1, -1):  # k = n-1, n-2, ..., 0
            p += coef * self.cp[k][history[(l-k):l]].prob(next_char)
            denom += coef
            coef *= self.q
        return p / denom

    def logprob(self, next_char, history):
        return -log(self.prob(next_char, history), 2)
    
    def entropy(self, text):
        n1 = self.n - 1
        text = (" " * n1) + text # pad text with blanks for initial history
        H = 0.0
        for k in xrange(n1, len(text)):
            H += self.logprob(text[k], text[(k-n1):k])
        return H

    def validate(self, text):
        '''
        This is an additional method not specified by the ModelI API.  It validates the n-gram
        model on a stretch of text, ensuring that (i) Pr(text) > 0 and (ii) that normalisation
        constraints are satisfied by the model for all histories that occur in the text.
        '''
        n1 = self.n - 1
        text = (" " * n1) + text # pad text with blanks for initial history
        checked_histories = {}   # don't check the same history twice (validation is expensive!)
        for k in xrange(n1, len(text)):
            history = text[(k-n1):k]
            if self.prob(text[k], history) <= 0:
                raise RuntimeError("Smoothing error: Pr(%s|%s) = 0" % (text[k], history))
            if history not in checked_histories:
                sum_p = 0.0
                for c in ALPHABET:
                    sum_p += self.prob(c, history)
                if abs(sum_p - 1.0) >= .0001:  # allow some rounding error
                    raise RuntimeError("Normalisation error: Sum Pr(*|%s) = %.6f (should be 1.0)" % (history, sum_p))		
                checked_histories[history] = 1
# -- end of class definition (SimpleNgramModel) --

def test():
    from nltk.corpus import brown
    from lm import ngram

    ## --> choose your own corpora here (make sure to use similar texts, so that n-gram models work well)
    train_corpus = " ".join(brown.words(categories="romance"))  # train models on romance
    devel_corpus = " ".join(brown.words(categories="humor"))    # optimise meta-parameters on humour
    # NB: we cannot just use <corpus>.raw() for an annotated corpus!

    ## --> reduce corpus size if your computer isn't fast enough
    # train_corpus = train_corpus[0:50000]
    # devel_corpus = devel_corpus[0:50000]

    ## --> increase this value in order to experiment with higher-order models
    n_max = 6

    print "Training data:    %d characters" % (len(train_corpus))
    print "Development data: %d characters" % (len(devel_corpus))
    train_corpus = ngram.cleanup(train_corpus)
    devel_corpus = ngram.cleanup(devel_corpus)
    train_fdata = ngram.collect_frequency_data(train_corpus, n_max)


    best_model = None
    best_entropy = 999
    for n in range(1, n_max + 1):
        model = ngram.SimpleNgramModel(train_fdata, n, 0.1)
        train_entropy = model.entropy(train_corpus) / len(train_corpus)  # measure per-character entropy for easier comparison
        devel_entropy = model.entropy(devel_corpus) / len(devel_corpus)
        print "%d-gram model (q=0.1):  training text H = %4.2f bits/char  devel text H = %4.2f bits/char" % (n, train_entropy, devel_entropy)
        if (devel_entropy < best_entropy):
            best_model = model
            best_entropy = devel_entropy

    print "Validating best model (%d-grams) with cross-entropy H = %.2f bits/char." % (best_model.n, best_entropy)
    best_model.validate(devel_corpus)
    
    best_model.prob('disliked', 'They neither liked nor')


