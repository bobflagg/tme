'''
Common utility functions supporting data management.
'''
from codecs import open as codecs_open
from nltk.tokenize import sent_tokenize, word_tokenize
import re

__all__ = [
    'prepare_document',
    'word_tokenize_doc',
    'write_utf_8_file',
]
BAD_WHITE_SPACE_PAT = r'\n|\r|\t'
BAD_WHITE_SPACE_RE = re.compile(BAD_WHITE_SPACE_PAT)


def open_utf_8_file(path):
    '''
    Returns a file descriptor for writing utf-8 encoded strings.
    '''
    fileObj = codecs_open(path, "w", "utf-8")
    return fileObj

def prepare_document(document):
    '''
    Returns a unicode string formed by removing "bad" white space from the 
    given document.
    '''
    if isinstance(document, unicode): document = document.encode('utf-8')
    return BAD_WHITE_SPACE_RE.sub(' ', document).strip().decode("utf-8")

def read_utf_8_file(path):
    '''
    Returns the contents of a utf-8 encoded file as a unicode string.
    '''
    fileObj = codecs_open(path, "r", "utf-8" )
    return fileObj.read()

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
    '''
    Writes the given unicode string to the file with the given path, using
    UTF-8 encoding.
    '''
    fileObj = codecs_open(path, "w", "utf-8" )
    fileObj.write(data)
    fileObj.close()