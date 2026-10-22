from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
@permission_classes([AllowAny])
def get_current_user(request):
    if request.user.is_authenticated:
        # If using django-allauth, the user's name/email is available on request.user
        return Response({
            "is_authenticated": True,
            "username": request.user.username,
            "name": request.user.first_name,
            "email": request.user.email,
        })
    return JsonResponse({"is_authenticated": False})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return redirect("/")


