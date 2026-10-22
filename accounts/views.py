from django.shortcuts import render, redirect
from django.contrib.auth import logout

from django.http import JsonResponse

def get_current_user(request):
    if request.user.is_authenticated:
        # If using django-allauth, the user's name/email is available on request.user
        return JsonResponse({
            "is_authenticated": True,
            "username": request.user.username,
            "name": request.user.first_name,
            "email": request.user.email,
        })
    return JsonResponse({"is_authenticated": False})
def logout_view(request):
    logout(request)
    return redirect("/")




