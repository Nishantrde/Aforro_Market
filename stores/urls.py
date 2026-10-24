from django.urls import path
from .views import get_product, get_store

urlpatterns = [
    path("products", get_product, name="get_product"),
    path("", get_store, name="get_store")
]

