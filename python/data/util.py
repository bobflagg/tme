'''
Common utility functions supporting data management.
'''
from codecs import open as codecs_open
from nltk.tokenize import sent_tokenize, word_tokenize

__all__ = [
    'word_tokenize_doc',
    'write_utf_8_file',
]

def tokenize_doc(document):    
    """
    Returns the list of tokenized sentences extracted from the given document.
        @param document: A valid UTF-8 encoded string.
    """
    sentences = sent_tokenize(document)
    tokenized_sentences = [word_tokenize(x) for x in sentences] 
    return tokenized_sentences
      
def word_tokenize_doc(document):    
    """
    Returns the list of tokens appearing in the given document.
        @param document: A valid UTF-8 encoded string.
    """
    return sum(tokenize_doc(document), [])

def write_utf_8_file(path, data):  
    fileObj = codecs_open(path, "w", "utf-8" )
    fileObj.write(data)
    fileObj.close()