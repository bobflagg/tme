from django.conf.urls.defaults import *
from piston.resource import Resource
from api.handlers import StatusHandler, TopicHandler

topic_handler = Resource(TopicHandler)
status_handler = Resource(StatusHandler)

urlpatterns = patterns('',
    url(r'^topic/(?P<id>[^/]+)/', topic_handler),
    url(r'^topics/', topic_handler),
    url(r'^status/', status_handler),
)