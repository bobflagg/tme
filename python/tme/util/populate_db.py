'''
import util.populate_db as pdb
pdb.populate()
reload(pdb)
'''
import os
import simplejson
from topics.models import Document

PROJECT_DIRECTORY = '/home/birksworks/Projects/Truonex/Assigning-Topic-Labels'
CORPUS_DIRECTORY = '%s/corpus' % PROJECT_DIRECTORY

TASK = [
    'populate',       # 0
][0]

def main():
    '''
    Convenience method to do preliminary testing.
    '''
    globals()[TASK]()

def populate():
    add_documents()
    
def add_documents():
    '''
    Populates tme database with current topic model data.
    '''
    print '--->> add_documents'
    # Remove old data.
    Document.objects.all().delete()
    f = open('%s/title-map.json' % CORPUS_DIRECTORY)
    title_map = simplejson.load(f) 
    f.close()
    file_list = os.listdir(CORPUS_DIRECTORY)
    for file_name in file_list:
        if file_name.endswith('txt'): 
            project_id = file_name[:-4]
            content = open(CORPUS_DIRECTORY+"/"+file_name).read()
            document = Document(
                title=title_map[project_id],
                project_id = project_id,
                content = content,
            )
            document.save()
      
if __name__ == "__main__":
    main()    
