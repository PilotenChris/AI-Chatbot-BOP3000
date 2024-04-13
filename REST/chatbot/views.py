from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import Feedback
from ..db_connection import collection
from AI_Chatbot.Chatbot import model

# Create your views here.

# Test 1
class FeedbackAPI(APIView):
    def post(self, request):
        serializer = Feedback(data=request.data)
        if serializer.is_valid():
            question = serializer.validated_data['question']
            response = serializer.validated_data['response']
            feedback = serializer.validated_data.get('feedback')
            # Save data to MongoDB collection
            collection.insert_one({
                'question': question,
                'response': response,
                'feedback': feedback
            })

            return Response({'Samtale og tilbakemelding er lagret i databasen'})
        else:
            return Response(serializer.errors, status=400)

# Test 2


class chatbotView(APIView):
    def post(self, request):
        user_input = request.data.get('text')
        # Processing user input with Llama2
        response_text = model.predict(user_input)
        # API response
        data = {'response': response_text}
        return Response(data)