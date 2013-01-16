from piston.handler import BaseHandler
from topics.models import Topic

class TopicHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Topic
    fields = ('topic_id', 'label', 'top_words')

    def read(self, request, id=None):
        if id:
            return Topic.objects.get(pk=id)
        else:
            return Topic.objects.all()
        
class StatusHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, id=None):
        return "OK"