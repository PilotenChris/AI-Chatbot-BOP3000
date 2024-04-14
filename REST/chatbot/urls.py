from django.urls import path
from .views import FeedbackAPI
from .views import ChatbotView

urlpatterns = [
    path('feedback/', FeedbackAPI.as_view()),
    path('chatbot/', ChatbotView.as_view())
]