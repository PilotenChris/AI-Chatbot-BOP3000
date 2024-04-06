from django.urls import path
from .views import FeedbackAPI

urlpatterns = [
    path('feedback/', FeedbackAPI.as_view()),
]