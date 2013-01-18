'''

'''
from codecs import open as codecs_open
import os
import simplejson
from db import DataManager as trDM
from db import MLDataManager as mlDM
from util import open_utf_8_file, prepare_document, read_utf_8_file, write_utf_8_file

HOME_DIRECTORY = '/home/birksworks/Projects/TME'
CORPUS_DIRECTORY = '%s/corpus' % HOME_DIRECTORY
MODEL_DIRECTORY = '%s/model' % HOME_DIRECTORY
PROCESSED_DIRECTORY =  '%s/html/processed' % HOME_DIRECTORY
MIN_NUMBER_OF_WORDS_IN_DESCRIPTION = 12

def main():
    ml_dbm = mlDM()
    tr_dbm = trDM()
    build_corpus(ml_dbm, tr_dbm)

def test_write(id):
    dbm = trDM()
    i = 0
    project = dbm.get_project(id)
    print project['id']
    doc_id = 'tr-%s' % project['id']
    dst_path = '%s/%s.txt' % (CORPUS_DIRECTORY, doc_id)
    src_path = '%s/%s.txt' % (PROCESSED_DIRECTORY, project['id'])
    if os.path.exists(src_path):
        print 'from file'
        data = read_utf_8_file(src_path)
    else:
        print 'from db'
        data = project['content']
    write_utf_8_file("/tmp/proj.txt", "%s||||%s||||%s||||%s\n" % (doc_id, project['title'].strip(), project['url'], prepare_document(data)))
    
def build_corpus(ml_dbm, tr_dbm):   
    print '--->> build_corpus'
    # remove old data:
    fileList = os.listdir(CORPUS_DIRECTORY)
    for fileName in fileList:
        os.remove(CORPUS_DIRECTORY+"/"+fileName)
    record_cnt = 0
    document_cnt = 0
    title_map = {}
    # Add all truonex projects to the corpus:
    titles = set({}) 
    sd_fp = open_utf_8_file("%s/src.info" % MODEL_DIRECTORY)
    for project in tr_dbm.get_project_data():
        record_cnt += 1
        if len(project['text']) >= MIN_NUMBER_OF_WORDS_IN_DESCRIPTION:
            document_cnt += 1
            title = project['title'].strip()
            titles.add(title.lower())
            doc_id = 'tr-%s' % project['id']
            title_map[doc_id] = title
            src_path = '%s/%s.txt' % (PROCESSED_DIRECTORY, project['id'])
            source = project['content']
            if os.path.exists(src_path):
                data = read_utf_8_file(src_path)
            else:
                data = project['content']
            write_utf_8_file('%s/%s.txt' % (CORPUS_DIRECTORY, doc_id), data)
            sd_fp.write("%s||||%s||||%s||||%s||||%s\n" % (doc_id, title, project['url'], prepare_document(source), prepare_document(data)))
    # Add all medialab projects to the corpus:
    _, projects = ml_dbm.get_project_data()
    for project in projects.values():
        record_cnt += 1
        title = project['name'].strip()
        if title.lower() in titles: continue
        document_cnt += 1
        titles.add(title.lower())
        doc_id = 'ml-%s' % project['id']
        title_map[doc_id] = title
        content = "%s.  %s" % (title, project['description'])
        write_utf_8_file('%s/%s.txt' % (CORPUS_DIRECTORY, doc_id), content)
        sd_fp.write("%s||||%s||||%s||||%s||||%s\n" % (doc_id, title, project['url'], prepare_document(content), prepare_document(content)))
    f = open('%s/title-map.json' % CORPUS_DIRECTORY, 'w')
    simplejson.dump(title_map, f, indent=4) 
    f.close()
    sd_fp.close()
    print "Processed %d records and generated %d documents." % (record_cnt, document_cnt)
    
if __name__ == "__main__":
    main()    
