import django
import json
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aforro_market.settings') # Replace with your actual project settings name
django.setup()

from stores.models import Product

def load_products():
    file_path = 'products.json'
    product_data = ""

    with open(file_path, 'r', encoding='utf-8') as f:
        product_data = json.load(f)

    for item in product_data:
        Product.objects.create(
            product_name=item['product_name'],
            category=item['category'],
            price=item['price']
        )


load_products()


