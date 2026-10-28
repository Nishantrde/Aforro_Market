from django.db import models
from accounts.models import Merchant
from django.conf import settings


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

class Order(models.Model):

    class Status(models.TextChoices):
        PLACED = 'PLACED'
        CONFIRMED = 'CONFIRMED'
        PACKED = 'PACKED'
        DELIVERED = 'DELIVERED'
        CANCELLED = 'CANCELLED'
        OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    store = models.ForeignKey(Store, on_delete=models.PROTECT, related_name='orders')
    status = models.CharField(max_length=250, choices=Status.choices, default=Status.PLACED)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order {self.id} by {self.user}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete = models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveBigIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return str(self.order)

class StoreProduct(models.Model):
    store = models.ForeignKey(Store, on_delete = models.CASCADE, related_name='store_items')
    product = models.ForeignKey(Product, on_delete = models.PROTECT, related_name='store_items')
    stock = models.PositiveBigIntegerField(default=0)

    class Meta:                                      
        constraints = [
            models.UniqueConstraint(
                fields=['store', 'product'],         
                name='unique_store_product',         
            )
        ]


    def __str__(self):
        return f"{self.store} - {self.product} ({self.stock})"

