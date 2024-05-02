import os
from django.utils import timezone

from dotenv import load_dotenv
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .Chatbot import get_response, get_case_response, feedback, sendEmail, introduce_chatbot
from rest_framework import status
from .models import ChatMessage
from .utils import start_new_session
from .Db import chatlog


load_dotenv()
current_datetime = timezone.datetime.now()

class InformationView(APIView):
    def post(self, request):
        sessionId = start_new_session()
        user_input = request.data.get('message')
        # Processing user input with Llama2
        response_text = get_response(user_input)
        # save chat log to the database
        chat_log = ChatMessage(sessionId=sessionId, user_input=user_input, response_text=response_text,
                                              timestamp=timezone.now())
        chat_log_dict = {
            'sessionId': sessionId,
            'user_input': chat_log.user_input,
            'response_text': chat_log.response_text,
            'timestamp': chat_log.timestamp
        }
        chatlog.insert_one(chat_log_dict)
        # API response
        data = {'response': response_text}
        return Response(data)


class ComplaintView(APIView):
    def post(self, request):
        sessionId = start_new_session()
        user_input = request.data.get('message')
        response_text = get_case_response(user_input)
        chat_log = ChatMessage(sessionId=sessionId,user_input=user_input, response_text=response_text,
                                              timestamp=timezone.now())
        chat_log_dict = {
            'sessionId': sessionId,
            'user_input': chat_log.user_input,
            'response_text': chat_log.response_text,
            'timestamp': chat_log.timestamp
        }
        chatlog.insert_one(chat_log_dict)
        data = {'response': response_text}
        return Response(data)

    """"
class ChatHistoryView(APIView):
    # Send chatlog to email view
    def sendEmail(self, request):
     # user email input
     user_input = request.data.get('text')
     # Retrieve chatlog from database

     # call sendEmail function
     result = sendEmail(user_input, chatlog)
     return Response({'request': result}, status=status.HTTP_200_OK) """

class FeedbackCheckView(APIView):
    def get(self, request):
        #is_feedback_allowed = os.getenv('FEEDBACK_OPEN')
        is_feedback_allowed = True
        return Response({'isFeedbackAllowed': is_feedback_allowed}, status=status.HTTP_200_OK)

class FeedbackSubmitView(APIView):
    def post(self, request):
        feedback_response = request.data.get('feedback')
        message_text = request.data.get('messages')
        feedback(message_text, feedback_response)
        return Response({'message': 'Feedback submitted successfully.'}, status=status.HTTP_200_OK)

class GreetingView(APIView):
    def get(self, request):
        greeting_text = introduce_chatbot()
        return Response({'greeting': greeting_text}, status=status.HTTP_200_OK)