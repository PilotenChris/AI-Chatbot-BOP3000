from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .Chatbot import model_dir, get_response, get_case_response, feedback, sendEmail
from rest_framework import status
from .models import ChatMessage

# Create your views here.


class ChatbotView(APIView):
    def post(self, request):
        user_input = request.data.get('text')
        # Processing user input with Llama2
        response_text = get_response(user_input)
        # save chat log to the database
        chat_log = ChatMessage.objects.create(user_input=user_input, response_text=response_text)
        # API response
        data = {'response': response_text}
        return Response(data)

    def post_case(self, request):
        user_input = request.data.get('text')
        response_text = get_case_response(user_input)
        chat_log = ChatMessage.objects.create(user_input=user_input, response_text=response_text)
        data = {'response': response_text}
        return Response(data)

    # Send chatlog to email view
    def sendEmail(self, request):
     # user email input
     user_input = request.data.get('text')
     # Retrieve chatlog from database
     chat_log_entry = ChatMessage.objects.all()
     chat_log = "\n".join([f"User input: {entry.user_input}, Response: {entry.response}" for entry in chat_log_entry])
     # call sendEmail function
     result = sendEmail(user_input, chat_log)
     return Response({'request': result}, status=status.HTTP_200_OK)

