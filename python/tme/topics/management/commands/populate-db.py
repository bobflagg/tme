from django.core.management.base import BaseCommand
from optparse import make_option
import os
import simplejson
from topics.models import Document, Phrase

PROJECT_DIRECTORY = '/home/birksworks/Projects/Truonex/Assigning-Topic-Labels'
CORPUS_DIRECTORY = '%s/corpus' % PROJECT_DIRECTORY
MODEL_DIRECTORY = '%s/model' % PROJECT_DIRECTORY

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
             '--d',
            action='store_true',
            default=False,
            help='Populate document table'),
        make_option(
             '--k',
            action='store_true',
            default=False,
            help='Populate key phrase table'),
        )
    help = 'Populates the database with new topic model data.'

    def handle(self, *args, **options):
        did_nothing = True
        if options['d']:
            did_nothing = False
            add_documents()
        if options['k']:
            did_nothing = False
            add_keyphrases()
        if did_nothing:
            add_documents()
            add_keyphrases()
    
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
