from rest_framework import serializers
from .models import Product, Store

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

class StoreSerializer(serializers.ModelSerializer):
    owner_username = serializers.SlugRelatedField(
        source = 'owner',
        slug_field = 'user__first_name',
        read_only = True
    )
    products = ProductSerializer(many=True, read_only=True)
    class Meta:
        model = Store
        fields = ["store_name", "owner_username", "products"]



