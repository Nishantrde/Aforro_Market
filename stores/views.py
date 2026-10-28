from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Store, Order, OrderItem, StoreProduct
from .serializer import ProductSerializer, StoreSerializer

from difflib import get_close_matches
from django.db import transaction
from decimal import Decimal
from collections import defaultdict

class OutOfStock(Exception):
    pass


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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    items = request.data.get('items', [])
    
    if not items:
        return Response({"error":"Empty cart"}, status=status.HTTP_400_BAD_REQUEST)
    
    lines_by_store = defaultdict(list)

    for item in items:
        # {"store_id": 1, "product_id": 3, "quantity": 2}
        
        store_id = item.get("store_id")
        product_id = item.get("product_id")
        quantity = item.get("quantity")
        
        store = Store.objects.filter(id = store_id).first()
        product = Product.objects.filter(id = product_id).first()

        if store is None:
                return Response({"error": "store not found"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return Response({'error':"quantity must be a whole number"}, status=status.HTTP_400_BAD_REQUEST)
        
        if quantity <= 0:
            return Response({"error":"quantity must be at least ONE"}, status.HTTP_400_BAD_REQUEST)

        # if store.products.filter(id=product_id).exists():
        #     lines_by_store[store].append((product, quantity))
        # else:
        #     return Response({'error':'product dose not exists in the store'}, status=status.HTTP_400_BAD_REQUEST)

        stock_row = StoreProduct.objects.filter(store = store, product = product).first()

        if stock_row is None:
            return Response({'error': 'this store does not sell this product'},
                            status=status.HTTP_400_BAD_REQUEST)

        if stock_row.stock < quantity:
            return Response({'error': f'only {stock_row.stock} left in stock'},
                            status=status.HTTP_400_BAD_REQUEST)

        lines_by_store[store].append((product, quantity))

    try:
        with transaction.atomic():
            created = []
            
            for store, lines in lines_by_store.items():
                total = Decimal('0')
                order = Order.objects.create(user = request.user, store = store)
                for product, quantity in lines:
                    # price = Decimal(str(product.price))
                    # OrderItem.objects.create(order = order, product = product, quantity = quantity, price = price)
                    # total += price*quantity
                    
                    row = StoreProduct.objects.select_for_update().get(store = store, product = product)
                    if row.stock < quantity:
                        raise OutOfStock(f"only {row.stock} left of {product.product_name}")
                    row.stock -= quantity
                    row.save()
                    price = Decimal(str(product.price))
                    OrderItem.objects.create(order = order, product = product, quantity = quantity, price = price)
                    total += price*quantity
                    

                created.append(
                    {
                        "id": order.id,                 
                        "store": store.store_name,                          
                        "status": order.status,         
                        "total": str(total),            
                    }
                )

    except OutOfStock as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    return Response(created, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    order = Order.objects.filter(id = order_id, user = request.user).first()

    if order is None:
        return Response({"error":"order not found"}, status=status.HTTP_404_NOT_FOUND)

    if order.status not in (Order.Status.PLACED, Order.Status.CONFIRMED):
        return Response({"error":f"order can't be cancelled because order is in {order.status}"}, status=status.HTTP_400_BAD_REQUEST)

    # order.status = Order.Status.CANCELLED
    # order.save()

    # return Response({"id":order.id, "status":order.status}, status=status.HTTP_200_OK)

    with transaction.atomic():
        locked = Order.objects.select_for_update().get(id=order.id)
        if locked.status not in (Order.Status.PLACED, Order.Status.CONFIRMED):
            return Response({"error": "order can't be cancelled"}, status=status.HTTP_400_BAD_REQUEST)
        for item in locked.items.all():
            row = StoreProduct.objects.select_for_update().get(store = locked.store, product = item.product)
            row.stock += item.quantity
            row.save()
        locked.status = Order.Status.CANCELLED
        locked.save()
    return Response({"id": locked.id, "status": locked.status}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def product_stores(request, product_id):
    rows = StoreProduct.objects.filter(product_id = product_id, stock__gt = 0).select_related('store')
    result = []
    for row in rows:
        result.append({"store_id": row.store_id, "store_name": row.store.store_name, "stock": row.stock})

    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_orders(request):
    orders = (Order.objects.filter(user=request.user)
          .select_related('store')
          .prefetch_related('items__product')
          .order_by('-created_at'))
    result = []
    for order in orders:
        items = []
        total = Decimal('0')
        for item in order.items.all():
            items.append({"name": item.product.product_name, "quantity": item.quantity, "price": str(item.price)})
            total += item.price * item.quantity

        result.append({
            "id": order.id,
            "store": order.store.store_name,
            "status": order.status,
            "created_at": order.created_at.isoformat(),
            "items": items,
            "total": str(total),
        })
    return Response(result)







