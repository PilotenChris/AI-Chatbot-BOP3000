from django.db import models
from .Db import db
# Create your models here.

# Collection to save the chatlog
chatlog_collection = db('Chatlog')


class ChatMessage(models.Model):
    sessionId = models.CharField(max_length=100)
    text = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.timestamp}: - text: {self.text} - response: {self.response}'

    # Collection to save the chatlog
    chatlog_collection = db('ChatLog')
