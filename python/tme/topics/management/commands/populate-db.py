from codecs import open as codecs_open
from django.core.management.base import BaseCommand
from optparse import make_option
import os
import simplejson
from corpus.models import Project
from topics.models import Document, Phrase, Topic

PROJECT_DIRECTORY = '/home/birksworks/Projects/Truonex/Assigning-Topic-Labels'
CORPUS_DIRECTORY = '%s/corpus' % PROJECT_DIRECTORY
MODEL_DIRECTORY = '%s/model' % PROJECT_DIRECTORY
TME_HOME = '/home/birksworks/Projects/TME'
TME_CORPUS_DIRECTORY = '%s/tme-corpus' % TME_HOME
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '--c',
            action='store_true',
            default=False,
            help='Populate corpus project table'),
        make_option(
            '--d',
            action='store_true',
            default=False,
            help='Populate document table'),
        make_option(
            '--e',
            action='store_true',
            default=False,
            help='Export project data for topic modeling'),
        make_option(
            '--k',
            action='store_true',
            default=False,
            help='Populate key phrase table'),
        make_option(
            '--t',
            action='store_true',
            default=False,
            help='Populate topic table'),
    )
    help = 'Populates the database with new topic model data.'

    def handle(self, *args, **options):
        did_nothing = True
        if options['c']:
            did_nothing = False
            add_projects()
        if options['d']:
            did_nothing = False
            add_documents()
        if options['e']:
            did_nothing = False
            export_projects()
        if options['k']:
            did_nothing = False
            add_keyphrases()
        if options['t']:
            did_nothing = False
            add_topics()
    
def add_projects():
    '''
    Adds project text to the tme database.
    
    Data is read from a file at
        ${TME_HOME}/model/src.info
    previously prepared by running
        ~/bin/build-corpus.sh 
    '''
    print '--->> add_projects'
    # Remove old data.
    Project.objects.all().delete()
    f = codecs_open('%s/model/src.info' % TME_HOME, "r", "utf-8" )
    for line in f:
        try:
            project_id, title, url, source, content = line.strip().split('||||')
            processed = False
            if 'ciid' in url: processed = True
            project = Project(
                project_id = project_id,
                title = title,
                url = url,
                source = source,
                content = content,
                processed = processed
            )
            project.save()
        except Exception, e:
            print 'failed for line:'
            print line
            print e.message
    f.close()
        
def add_documents():
    '''
    Adds corpus documents to the tme database.
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
    
def add_keyphrases():
    '''
    Adds topic keyphrases to the tme database.
    '''
    print '--->> add_keyphrases'
    # Remove old data.
    Phrase.objects.all().delete()
    tpf = open("%s/top-words.txt" % MODEL_DIRECTORY)
    for line in tpf.read().split('\n')[1:-1]:
        _, type, keyphrase, _ = line.split('\t')
        if type == 'n': 
            keyphrase = keyphrase.replace('_', ' ')
            phrase = Phrase(
                phrase = keyphrase
            )
            phrase.save()
    
def add_topics():
    '''
    Adds topics to the tme database.
    '''
    print '--->> add_topics'
    # Remove old data.
    Topic.objects.all().delete()
    tpf = open("%s/top-words.txt" % MODEL_DIRECTORY)
    current_topic = -1
    cnt = 0
    for line in tpf.read().split('\n')[1:-1]:
        topic, type, token, probability = line.split('\t')
        if type == 'u': 
            keyphrase = keyphrase.replace('_', ' ')
            phrase = Phrase(
                phrase = keyphrase
            )
            phrase.save()

def add_topics():
    '''
    Adds topics to the tme database.
    '''
    print '--->> add_topics'
    # Remove old data.
    Topic.objects.all().delete()
    tpf = open("%s/top-words.txt" % MODEL_DIRECTORY)
    ignore = True
    current_topic = -1
    tokens = []
    for line in tpf.read().split('\n')[1:-1]:
        topic_id, type, token, probability = line.split('\t')
        if ignore and topic_id == current_topic: continue
        current_topic = topic_id
        ignore = False
        if type == 'u': 
            tokens.append(token)
            if len(tokens) == 3:
                top_words="{%s}" % ", ".join(tokens)
                topic = Topic(topic_id=topic_id, top_words=top_words)
                topic.save()
                tokens = []
                ignore = True
                print topic_id, '-->>', top_words
            
    
def export_projects():
    '''
    Exports project data for topic modeling.
    '''
    print '--->> export_projects'
    # Remove old data.
    fileList = os.listdir(TME_CORPUS_DIRECTORY)
    for fileName in fileList:
        os.remove(TME_CORPUS_DIRECTORY+"/"+fileName)
    title_map = {}
    for project in Project.objects.all():
        fp = codecs_open('%s/%s.txt' % (TME_CORPUS_DIRECTORY, project.project_id), "w", "utf-8" )
        fp.write(project.content)
        fp.close()
        title_map[project.project_id] = project.title
    f = open('%s/title-map.json' % TME_CORPUS_DIRECTORY, 'w')
    simplejson.dump(title_map, f, indent=4) 
    f.close()
