from django.db import models

# Create your models here.
class ChatMessage(models.Model):
    text = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.timestamp}: - text: {self.text} - response: {self.response}'