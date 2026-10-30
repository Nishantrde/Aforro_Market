from django.urls import path
from .views import get_product, get_store, place_order, cancel_order, product_stores, my_orders, update_order_status, merchant_orders

urlpatterns = [
    path("products", get_product, name="get_product"),
    path("", get_store, name="get_store"),
    path("orders", place_order, name="place_order"),
    path("orders/<int:order_id>/cancel", cancel_order, name="cancel_order"),
    path("products/<int:product_id>/stores", product_stores, name="product_stores"),
    path("orders/list", my_orders, name="my_orders"),
    path("orders/<int:order_id>/status", update_order_status, name="update_order_status"),
    path("merchant/orders", merchant_orders, name="merchant_orders"),
]

