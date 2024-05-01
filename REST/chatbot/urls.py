from django.urls import path
from .views import ChatbotView, FeedbackCheckView, FeedbackSubmitView

urlpatterns = [
    path('chatbot/', ChatbotView.as_view()),
    path('feedback/check/', FeedbackCheckView.as_view()),
    path('feedback/', FeedbackSubmitView.as_view())
]