from django.db import models
from accounts.models import Merchant

class Product(models.Model):
    product_name = models.CharField(max_length=250, default="product-name")
    category = models.CharField(max_length=250, default="category")
    price = models.FloatField(default=10.0)

    def __str__(self):
        return str(self.product_name) 

class Store(models.Model):
    owner = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='stores')
    store_name = models.CharField(max_length=250, default="store")
    address = models.TextField(blank=True, null=True, default="Dhanbad")
    created_at = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField(Product, blank=True, related_name="stores")

    def __str__(self):
        return str(self.store_name)
     


