from django.db import models

class Project(models.Model):
    project_id = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    source = models.TextField()
    content = models.TextField()
    url = models.URLField(blank=True, default='')
    processed = models.BooleanField(default=False)
    def __unicode__(self):       
        return "[%s] %s" % (self.project_id, self.title)
        #return '<a href="%s" target="_blank">[%s] %s</a>' % (self.url, self.project_id, self.title)
