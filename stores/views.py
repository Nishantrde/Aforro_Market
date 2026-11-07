from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Store, Order, OrderItem, StoreProduct, IdempotencyKey
from .serializer import ProductSerializer, StoreSerializer

from difflib import get_close_matches
from django.db import transaction, IntegrityError
from decimal import Decimal
from collections import defaultdict

from django.core.cache import cache
import warnings

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from accounts.models import DeliveryPartner
from .locations import locations
from .matching import nearest


def broadcast_stock(store_id, product_id, stock):
    try:
        layer = get_channel_layer()
        async_to_sync(layer.group_send)("stock", {
            "type": "stock.update",
            "store_id": store_id,
            "product_id": product_id,
            "stock": stock,
        })
    except Exception as e:
        warnings.warn(f"Stock broadcast failed: {e}")


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
@permission_classes([AllowAny])# show all the products if the user is not loged in
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

    #if data was None, not cached or got expired set the cache for 60 sec after Serializing it
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
    items = request.data.get('items', [])# if the item is not provided return a []
    
    if not items:# if cart was empty return 400 bad request
        return Response({"error":"Empty cart"}, status=status.HTTP_400_BAD_REQUEST)

    # to store (product and quantity) value in "Store" key 
    lines_by_store = defaultdict(list)# using the default dict because some time we have to make keys and append the list at the same time even if the dose not exists

    for item in items:
        
        store_id = item.get("store_id")
        product_id = item.get("product_id")
        quantity = item.get("quantity")
        
        store = Store.objects.filter(id = store_id).first()
        product = Product.objects.filter(id = product_id).first()

        if store is None:
                return Response({"error": "store not found"}, status=status.HTTP_400_BAD_REQUEST)

        # if quantity was a char or str like ("ONE", "FIVE") return Value Error
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return Response({'error':"quantity must be a whole number"}, status=status.HTTP_400_BAD_REQUEST)
        
        if quantity <= 0:
            return Response({"error":"quantity must be at least ONE"}, status.HTTP_400_BAD_REQUEST)

        # find if the the product and the store exists
        stock_row = StoreProduct.objects.filter(store = store, product = product).first()


        if stock_row is None:
            return Response({'error': 'this store does not sell this product'},
                            status=status.HTTP_400_BAD_REQUEST)

        if stock_row.stock < quantity:
            return Response({'error': f'only {stock_row.stock} left in stock'},
                            status=status.HTTP_400_BAD_REQUEST)

        lines_by_store[store].append((product, quantity))
        # (eg)lines_by_store = {
        #         Store(id=1): [
        #             (Milk, 2),
        #             (Sugar, 1)
        #         ],

        #         Store(id=2): [
        #             (Rice, 3)
        #         ]
        #     }

    try:
        with transaction.atomic():# protect our database to be left at an incomplete state 
            created = []

            # sorts the list of items in "lines_by_store" by their store id and then store id is extracted by store and product list is extracted by lines
            for store, lines in sorted(lines_by_store.items(), key=lambda pair: pair[0].id): 

                total = Decimal('0')

                # Creating orders
                order = Order.objects.create(user = request.user, store = store)

                #sorts the products according to product id and prduct and quantity is extracted respectively
                for product, quantity in sorted(lines, key=lambda line: line[0].id):

                    # select the particular product row and lock it until the customer has pursched it (until the transaction is over)
                    row = StoreProduct.objects.select_for_update().get(store = store, product = product)

                    if row.stock < quantity:
                        # raise exceptions here and stops the block here
                        raise OutOfStock(f"only {row.stock} left of {product.product_name}")
                    
                    row.stock -= quantity
                    row.save()

                    # broadcast stock on transaction compleations
                    transaction.on_commit(
                        lambda s=store.id, p=product.id, st=row.stock: broadcast_stock(s, p, st)
                    )

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

            # create IdempotencyKey to track Duplicate order request
            IdempotencyKey.objects.create(user=request.user, key=key, response=created)

    except OutOfStock as e:# catches the "OutOfStock" exception which was raise above return "Out of stock" Responce
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except IntegrityError:# raises when the order alredy existed
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

        # we have used "select_for_update" so that if the customers cancels the order twice the row of the first request gets locked and then canceled, after that the second request will be invalid because the order is already CANCELED and also they are not in PLACED or CONFIRMED state
        locked = Order.objects.select_for_update().get(id=order.id)

        if locked.status not in (Order.Status.PLACED, Order.Status.CONFIRMED):
            return Response({"error": "order can't be cancelled"}, status=status.HTTP_400_BAD_REQUEST)
        
        for item in locked.items.all():# get all the OrderItems from "locked" through "related_name" which is set as "items" in OrderItem model
            row = StoreProduct.objects.select_for_update().get(store = locked.store, product = item.product)
            row.stock += item.quantity
            row.save()
            transaction.on_commit(
                lambda s=locked.store_id, p=item.product_id, st=row.stock: broadcast_stock(s, p, st)
            )
        locked.status = Order.Status.CANCELLED
        locked.save()

    return Response({"id": locked.id, "status": locked.status}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def product_stores(request, product_id):
    rows = StoreProduct.objects.filter(product_id = product_id, stock__gt = 0).select_related('store')# "__gt" is just 'greater than' (stock > 0) 
    result = []
    for row in rows:
        result.append({"store_id": row.store_id, "store_name": row.store.store_name, "stock": row.stock})

    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_orders(request):
    orders = (Order.objects.filter(user=request.user)
          .select_related('store')
          .prefetch_related('items__product')# fetch all the products from the order
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
    order = Order.objects.select_for_update().get(id=order.id)
    if not can_move(order.status, new_status):
        return Response({"error": f"can't move from {order.status} to {new_status}"}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        order = Order.objects.select_for_update().get(id=order.id)   # lock the order row
        # TODO: re-check can_move(order.status, new_status) after the lock
        order.status = new_status
        order.save()

        if new_status == Order.Status.PACKED:
            store = order.store
            if store.latitude is not None and store.longitude is not None:
                try:
                    riders = locations.nearby(store.latitude, store.longitude)
                except Exception as e:
                    warnings.warn(f"Rider lookup failed: {e}")
                    riders = []                
                while riders:
                    chosen_id = nearest(riders, store.latitude, store.longitude)
                    rider = DeliveryPartner.objects.select_for_update().filter(id=chosen_id, online=True).first()
                    busy = rider is None or Order.objects.filter(
                        partner=rider,
                        status__in=[Order.Status.PACKED, Order.Status.OUT_FOR_DELIVERY],
                    ).exclude(id=order.id).exists()
                    if not busy:
                        order.partner = rider
                        order.save()
                        break
                    riders = [r for r in riders if r[0] != chosen_id]   # try the next nearest

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
        transaction.on_commit(lambda: broadcast_stock(store.id, row.product_id, row.stock))

    return Response({"store_id": store.id, "product_id": product_id, "stock": row.stock})

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

@api_view(['GET'])
@permission_classes([AllowAny])
def all_stock(request):
    rows = StoreProduct.objects.values("store_id", "product_id", "stock")
    return Response(list(rows))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def partner_online(request):
    partner = DeliveryPartner.objects.filter(user=request.user).first()
    if partner is None:
        return Response({"error": "not a delivery partner"}, status=status.HTTP_404_NOT_FOUND)

    try:
        lat = float(request.data.get("lat"))
        lng = float(request.data.get("lng"))
    except (ValueError, TypeError):
        return Response({"error": "lat and lng must be numbers"}, status=status.HTTP_400_BAD_REQUEST)

    partner.online = True
    partner.save()
    locations.update(partner.id, lat, lng)      # <- your first line goes here
    return Response({"online": True})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def partner_offline(request):
    partner = DeliveryPartner.objects.filter(user=request.user).first()
    if partner is None:
        return Response({"error": "not a delivery partner"}, status=status.HTTP_404_NOT_FOUND)
    partner.online = False
    partner.save()
    try:
        locations.remove(partner.id)
    except Exception as e:
        warnings.warn(f"Could not remove rider location: {e}")
    return Response({"online": False})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def partner_order(request):
    partner = DeliveryPartner.objects.filter(user=request.user).first()
    if partner is None:
        return Response({"error": "not a delivery partner"}, status=status.HTTP_404_NOT_FOUND)
    order = (Order.objects
             .filter(partner=partner, status__in=[Order.Status.PACKED, Order.Status.OUT_FOR_DELIVERY])
             .select_related('store')
             .first())
    if order is None:
        return Response(None)
    return Response({"id": order.id, "store": order.store.store_name, "status": order.status})




