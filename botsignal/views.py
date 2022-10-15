from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
"""
from .serializers import SignalModelSerializer
# Create your views here.


class SignalView(APIView):
    def post(self,request):
        serializer = SignalModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("success", status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""
