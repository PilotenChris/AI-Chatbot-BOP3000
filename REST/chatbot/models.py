from django.db import models
# Create your models here.



class ChatMessage(models.Model):
    user_input = models.TextField()
    response_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.timestamp}: - text: {self.user_input} - response: {self.response_text}'

