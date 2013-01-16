from django.db import models

class Document(models.Model):
    project_id = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    content = models.TextField()
    url = models.URLField(blank=True, default='')
    
class Token(models.Model):
    token = models.CharField(max_length=30)
    
class Phrase(models.Model):
    phrase = models.CharField(max_length=123)

class Topic(models.Model):
    topic_id = models.IntegerField(max_length=20)
    label = models.CharField(max_length=100)
    top_words = models.CharField(max_length=100)
    
class TokenScore(models.Model):
    topic = models.ForeignKey(Topic)
    token = models.ForeignKey(Token)
    score = models.FloatField()
    
class TopicScore(models.Model):
    document = models.ForeignKey(Document)
    topic = models.ForeignKey(Topic)
    score = models.FloatField()
