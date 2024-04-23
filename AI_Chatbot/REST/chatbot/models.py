from django.db import models

# Create your models here.
class ChatMessage(models.Model):
    text = models.TextField()
    response = models.TextField()