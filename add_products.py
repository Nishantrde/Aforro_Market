import os
import random

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aforro_market.settings")
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Merchant
from stores.models import Product, Store, StoreProduct

random.seed(42)
User = get_user_model()

CATALOG = {
    "Dairy": [("Milk 500ml", 28), ("Curd 400g", 35), ("Paneer 200g", 90), ("Butter 100g", 58)],
    "Fruits": [("Banana 1 dozen", 60), ("Apple 1kg", 160), ("Orange 1kg", 90), ("Grapes 500g", 80)],
    "Vegetables": [("Tomato 1kg", 40), ("Onion 1kg", 35), ("Potato 1kg", 30), ("Carrot 500g", 32)],
    "Bakery": [("Bread Loaf", 40), ("Brown Bread", 50), ("Pav 6 pcs", 30)],
    "Snacks": [("Potato Chips", 20), ("Biscuits Pack", 30), ("Namkeen 200g", 55)],
    "Beverages": [("Orange Juice 1L", 110), ("Tea Powder 250g", 130), ("Soda 750ml", 40)],
    "Groceries": [("Basmati Rice 1kg", 120), ("Toor Dal 1kg", 150), ("Atta 5kg", 240), ("Eggs 12 pcs", 84)],
    "Home": [("Dish Soap", 45), ("Detergent 1kg", 110), ("Toothpaste", 85)],
}

STORES = [
    ("demo_merchant1", "Sharma Kirana", "MG Road, Bengaluru"),
    ("demo_merchant2", "Fresh Mart", "Indiranagar, Bengaluru"),
    ("demo_merchant3", "Daily Needs", "Koramangala, Bengaluru"),
]

# products
products = []
for category, items in CATALOG.items():
    for name, price in items:
        p, _ = Product.objects.get_or_create(
            product_name=name, defaults={"category": category, "price": price}
        )
        products.append(p)

# fake merchants and stores
stores = []
for username, store_name, address in STORES:
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password("demo12345")
        user.save()
    merchant, _ = Merchant.objects.get_or_create(user=user)
    store, _ = Store.objects.get_or_create(
        owner=merchant, store_name=store_name, defaults={"address": address}
    )
    stores.append(store)

# stock: each store sells about 70% of products
for store in stores:
    for product in products:
        if random.random() < 0.7:
            StoreProduct.objects.get_or_create(
                store=store, product=product,
                defaults={"stock": random.choice([0, 3, 5, 12, 20, 30, 40])},
            )
            store.products.add(product)

print(f"Done: {Product.objects.count()} products, {Store.objects.count()} stores, "
      f"{StoreProduct.objects.count()} stock rows")
