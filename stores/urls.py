from django.urls import path
from .views import get_product, get_store, place_order, cancel_order

urlpatterns = [
    path("products", get_product, name="get_product"),
    path("", get_store, name="get_store"),
    path("orders", place_order, name="place_order"), 
    path("orders/<int:order_id>/cancel", cancel_order, name="cancel_order"),
]

