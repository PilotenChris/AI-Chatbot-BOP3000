from django.urls import path
from .views import InformationView, ComplaintView, FeedbackCheckView, FeedbackSubmitView, GreetingView, EmailSenderView

urlpatterns = [
    path('information/', InformationView.as_view()),
    path('complaint/', ComplaintView.as_view()),
    path('send_email/', EmailSenderView.as_view()),
    path('feedback/check/', FeedbackCheckView.as_view()),
    path('feedback/', FeedbackSubmitView.as_view()),
    path('greeting/', GreetingView.as_view())
]