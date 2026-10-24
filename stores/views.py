from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Store
from .serializer import ProductSerializer, StoreSerializer

@api_view(['GET'])
@permission_classes([AllowAny])#only for testing
def get_product(request):
    product = Product.objects.all()
    serializer = ProductSerializer(product, many = True)# get all produts required feild
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_store(request):
    store = Store.objects.all()
    serializer = StoreSerializer(store, many = True)

    return Response(serializer.data)
    






