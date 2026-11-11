from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Store, Order, OrderItem, StoreProduct, IdempotencyKey
from .serializer import ProductSerializer, StoreSerializer

from .cache_location import geoHash

from difflib import get_close_matches
from django.db import transaction, IntegrityError
from decimal import Decimal
from collections import defaultdict

from django.core.cache import cache
import warnings


class OutOfStock(Exception):
    pass

#stores the upcoming status as a value and current status as a key (current_status:upcoming_status)
ALLOWED = {
    "PLACED": ["CONFIRMED"],
    "CONFIRMED": ["PACKED"],
    "PACKED": ["OUT_FOR_DELIVERY"],
    "OUT_FOR_DELIVERY": ["DELIVERED"],
}

#varifies that if 'new_status' is the value of the key 'current'
def can_move(current, new_status):
    return new_status in ALLOWED.get(current, [])

@api_view(['GET'])
@permission_classes([AllowAny])#all show the products if the user is not loged in
def get_product(request):
    q = str(request.query_params.get('q',''))
    
    if q:# get close match of product
        products = Product.objects.all()
        product_list = []
        for product in products:
            words = product.product_name.lower().split()
    
            if get_close_matches(q, words) != []:
                product_list.append(product)
        return Response(ProductSerializer(product_list, many=True).data)

    #cache the data in upstash Redis
    data = None
    #Get the cache from Redis or else throw warning
    try:
        data = cache.get("products:all")
    except Exception as e:
        warnings.warn(f"Cache unable to get the data {e}")

    #if data was None, not cached or got expired set the cache for 60 sec by finding it from Serializer
    if data is None:
        products = Product.objects.all()
        data = list(ProductSerializer(products, many = True).data)
        try:
            cache.set('products:all', data, 60)
        except Exception as e:
            warnings.warn(f"Cache unable to set the data {e}")
    return Response(data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_store(request):
    store = Store.objects.all()
    serializer = StoreSerializer(store, many = True)

    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])# only authenticated users could place the order
def place_order(request):

    # To prevent duplicate orders we are using Idempotency key which we will from React frontend 
    key = request.headers.get("Idempotency-Key")
    if not key:# if key is not present we will send 400 status code 
        return Response({"error": "Idempotency-Key header required"}, status=status.HTTP_400_BAD_REQUEST)

    # it searches the key with the user if it exists we will return the saved responce othervise we will create IdempotencyKey object for the order
    saved = IdempotencyKey.objects.filter(user=request.user, key=key).first()
    if saved:
        return Response(saved.response, status=200)


    #collect the list of product with store and quantity {"store_id": 1, "product_id": 10, "quantity": 2},
    items = request.data.get('items', [])
    
    if not items:# if cart was empty return 400 bad request
        return Response({"error":"Empty cart"}, status=status.HTTP_400_BAD_REQUEST)

    
    lines_by_store = defaultdict(list)# using the default dict because some time we have to make keys and append the list at the same time even if the dose not exists

    for item in items:
        
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
            
            for store, lines in sorted(lines_by_store.items(), key=lambda pair: pair[0].id):
                total = Decimal('0')
                order = Order.objects.create(user = request.user, store = store)

                for product, quantity in sorted(lines, key=lambda line: line[0].id):
                    
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
            IdempotencyKey.objects.create(user=request.user, key=key, response=created)

    except OutOfStock as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except IntegrityError:
        saved = IdempotencyKey.objects.filter(user=request.user, key=key).first()
        if saved:
            return Response(saved.response, status=200)
        raise

    return Response(created, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    order = Order.objects.filter(id = order_id, user = request.user).first()

    if order is None:
        return Response({"error":"order not found"}, status=status.HTTP_404_NOT_FOUND)

    if order.status not in (Order.Status.PLACED, Order.Status.CONFIRMED):
        return Response({"error":f"order can't be cancelled because order is in {order.status}"}, status=status.HTTP_400_BAD_REQUEST)


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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    new_status = request.data.get('status')

    order = Order.objects.filter(id=order_id, store__owner__user=request.user).first()
    if order is None:
        return Response({"error": "order not found"}, status=status.HTTP_404_NOT_FOUND)

    if not can_move(order.status, new_status):
        return Response({"error": f"can't move from {order.status} to {new_status}"}, status=status.HTTP_400_BAD_REQUEST)

    order.status = new_status
    order.save()
    return Response({"id": order.id, "status": order.status})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def merchant_orders(request):

    orders = (Order.objects.filter(store__owner__user=request.user)
          .select_related('store', 'user')
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
            "customer": order.user.username,
            "store": order.store.store_name,
            "status": order.status,
            "created_at": order.created_at.isoformat(),
            "items": items,
            "total": str(total),
        })
        
    return Response(result)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_stock(request):
    store_id = request.data.get('store_id')
    product_id = request.data.get('product_id')
    new_stock = request.data.get('stock')
    try:
        new_stock = int(new_stock)
    except (ValueError, TypeError):
        return Response({"error": "stock must be a whole number"}, status=status.HTTP_400_BAD_REQUEST)

    if new_stock < 0:
        return Response({"error": "stock can't be negative"}, status=status.HTTP_400_BAD_REQUEST)
    
    store = Store.objects.filter(id=store_id, owner__user=request.user).first()

    if store is None:
        return Response({"error":"store not found"}, status=status.HTTP_404_NOT_FOUND) 

    with transaction.atomic():
        row = StoreProduct.objects.select_for_update().filter(store=store, product_id=product_id).first()
        if row is None:
            return Response({"error":"product not sold here"}, status=status.HTTP_404_NOT_FOUND) 
        row.stock = new_stock
        row.save()

    return Response({"store_id": store.id, "product_id": product_id, "stock": row.stock}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def merchant_stock(request):
    rows = (StoreProduct.objects
            .filter(store__owner__user=request.user)
            .select_related('store', 'product')
            .order_by('store_id', 'product__product_name'))
    stockList = []
    for row in rows:
        stockList.append({"store_id": row.store_id, "store": row.store.store_name,
       "product_id": row.product_id, "name": row.product.product_name,
       "stock": row.stock})
    return Response(stockList)

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def online_partners(request):
    if request.method == 'POST':
        location = request.data.get("location")
        try:
            hashCode = geoHash(location)
            print(hashCode)
            return Response({"hash_code":hashCode}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"error":str(e)}, status=status.HTTP_404_NOT_FOUND)
        
    if request.method == 'GET':
        hashCode = request.query_params.get("location")
        try:
            data = cache.get(f"{hashCode}")
            if data is None:
                return Response(
                    {"error": "No location found in cache"},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response({"location":data},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_404_NOT_FOUND)


