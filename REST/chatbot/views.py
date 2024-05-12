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


load_dotenv()
current_datetime = timezone.datetime.now()

class InformationView(APIView):
    def post(self, request):
        user_input = request.data.get('message')
        # Processing user input with Llama2
        response_text = get_response(user_input)

        # API response
        data = {'response': response_text}
        return Response(data)


class ComplaintView(APIView):
    def post(self, request):
        user_input = request.data.get('message')
        response_text = get_case_response(user_input)
        data = {'response': response_text}
        return Response(data)


class EmailSenderView(APIView):
    # Send chatlog to email view
    def post(self, request):
        # user email input
        email_address = request.data.get('email')
        # Retrieve chatlog from database
        chatlog = request.data.get('messages')
        # formats the message and calls sendEmail function
        sendEmail(email_address, '\n'.join([f"{msg['from']}: {msg['text']}" for msg in chatlog]))
        return Response({'request': ''}, status=status.HTTP_200_OK)

class FeedbackCheckView(APIView):
    def get(self, request):
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