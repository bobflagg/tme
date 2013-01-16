from BeautifulSoup import BeautifulSoup
from codecs import open as codecs_open
from db import DataManager
import psycopg2 #@UnresolvedImport
#import xml.etree.cElementTree as etree
import requests
from requests import ConnectionError
from time import sleep

HOME_DIR = '/home/birksworks/Projects/TME'
   
def scrape(project_id, source_url):
    print source_url
    r = requests.get(source_url)
    fp = codecs_open("%s/html/%s.html" % (HOME_DIR, project_id), "w", "utf-8" )
    soup = BeautifulSoup(r.text)
    text = " ".join(x.text for x in soup.find("div", {'class':"post"}).findAll("p"))

    #content = etree.fromstring(r.text,encoding="utf-8").text_content(encoding="utf-8")
    fp.write(text)
    fp.close()
    
def scrape_ciid():
    dbm = DataManager()
    for pid, source_url in dbm.get_ciid_projects():
        print '\n-----\n'
        print "working on project %s" % pid
        print "url: %s" % source_url
        print "====="
        try:
            fp = codecs_open("%s/html/ciid/%s.html" % (HOME_DIR, pid), "r", "utf-8" )
            html = fp.read()
            fp.close()
            soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
            fp = codecs_open("%s/html/processed/%s.txt" % (HOME_DIR, pid), "w", "utf-8" )
            text = " ".join(x.text for x in soup.find("div", {'class':"post"}).findAll("p"))
            fp.write(text)
            fp.close()
            print text
            sleep(2)
        except Exception, e:
            print "failed"
            print e.message()
    
def collect_source_data():
    dbm = DataManager()
    for pid, source_url in dbm.get_project_source():
        print "working on project %s" % pid
        print "url: %s" % source_url
        try:
            r = requests.get(source_url)
            fp = codecs_open("%s/html/%s.html" % (HOME_DIR, pid), "w", "utf-8" )
            fp.write(r.text)
            fp.close()
            sleep(1)
        except ConnectionError, e:
            print "failed"
            print e.message

