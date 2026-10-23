from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include("allauth.urls")),
    path("user/", include("accounts.urls")),
    path("store/", include("stores.urls")),
    path('', TemplateView.as_view(template_name='index.html')),
    
]
