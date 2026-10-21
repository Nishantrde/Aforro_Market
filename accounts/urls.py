from django.urls import path
from . import views

urlpatterns = [
    path("api/user/me", views.get_current_user, name='current_user'),
    path("logout", views.logout_view),
]

