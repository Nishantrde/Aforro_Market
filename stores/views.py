from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Store
from .serializer import ProductSerializer, StoreSerializer

from difflib import get_close_matches

@api_view(['GET'])
@permission_classes([AllowAny])#only for testing
def get_product(request):
    q = str(request.query_params.get('q',''))
    products = Product.objects.all()
    if q:
        product_list = []
        for product in products:
            words = product.product_name.lower().split()
    
            if get_close_matches(q, words) != []:
                product_list.append(product)

        serializer = ProductSerializer(product_list, many = True)
        return Response(serializer.data)
        
    serializer = ProductSerializer(products, many = True)# get all produts required feild
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_store(request):
    store = Store.objects.all()
    serializer = StoreSerializer(store, many = True)

    return Response(serializer.data)
    






