from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .Chatbot import model_dir, get_response

# Create your views here.


class ChatbotView(APIView):
    def post(self, request):
        user_input = request.data.get('text')
        # Processing user input with Llama2
        response_text = get_response(user_input, model_dir)
        # API response
        data = {'response': response_text}
        return Response(data)