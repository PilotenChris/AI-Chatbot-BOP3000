from django.urls import path
from .views import InformationView, ComplaintView, FeedbackCheckView, FeedbackSubmitView, GreetingView, ChatHistoryView

urlpatterns = [
    path('information/', InformationView.as_view()),
    path('complaint/', ComplaintView.as_view()),
    ##path('chathistory/', ChatHistoryView.as_view()),
    path('send_email/', ChatHistoryView.as_view(), name='send_email'),
    path('feedback/check/', FeedbackCheckView.as_view()),
    path('feedback/', FeedbackSubmitView.as_view()),
    path('greeting/', GreetingView.as_view())
]