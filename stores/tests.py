from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import Merchant
from .models import Order, OrderItem, Product, Store, StoreProduct

class PlaceOrderTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.customer = User.objects.create_user(username="nishant", password="pass12345")
        shopkeeper = User.objects.create_user(username="shopkeeper", password="pass12345")
        merchant = Merchant.objects.create(user=shopkeeper)

        self.store1 = Store.objects.create(owner=merchant, store_name="Sharma Kirana")
        self.store2 = Store.objects.create(owner=merchant, store_name="Fresh Mart")

        self.milk = Product.objects.create(product_name="Milk", category="Groceries", price=2.50)
        self.bread = Product.objects.create(product_name="Bread", category="Groceries", price=3.20)
        self.soap = Product.objects.create(product_name="Soap", category="Home", price=1.00)

        self.store1.products.add(self.milk, self.bread)
        self.store2.products.add(self.soap)

        StoreProduct.objects.create(store = self.store1, product = self.milk, stock = 10)
        StoreProduct.objects.create(store = self.store1, product = self.bread, stock = 10)
        StoreProduct.objects.create(store = self.store2, product = self.soap, stock = 10)

        self.client = APIClient()
        self.client.force_login(self.customer)

    def post_cart(self, items):
        return self.client.post("/store/orders", {"items": items}, format="json")

    def test_valid_order_has_correct_total(self):
        response = self.post_cart([
            {"store_id": self.store1.id, "product_id": self.milk.id, "quantity": 2},
            {"store_id": self.store1.id, "product_id": self.bread.id, "quantity": 1},
        ])
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Decimal(response.json()[0]["total"]), Decimal("8.20"))
        self.assertEqual(response.json()[0]["status"], "PLACED")

    def test_cart_from_two_stores_creates_two_orders(self):
        response = self.post_cart([
            {"store_id": self.store1.id, "product_id": self.milk.id, "quantity": 1},
            {"store_id": self.store2.id, "product_id": self.soap.id, "quantity": 3},
        ])
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(Order.objects.count(), 2)

    def test_price_is_snapshotted_on_the_order_item(self):
        self.post_cart([{"store_id": self.store1.id, "product_id": self.milk.id, "quantity": 1}])
        self.milk.price = 99.0
        self.milk.save()
        item = OrderItem.objects.get()
        self.assertEqual(item.price, Decimal("2.50"))

    def test_empty_cart_is_rejected(self):
        response = self.post_cart([])
        self.assertEqual(response.status_code, 400)

    def test_product_not_sold_by_store_is_rejected(self):
        response = self.post_cart([{"store_id": self.store1.id, "product_id": self.soap.id, "quantity": 1}])
        self.assertEqual(response.status_code, 400)

    def test_bad_quantity_is_rejected(self):
        for bad in [0, -3, "abc", None]:
            with self.subTest(quantity=bad):
                response = self.post_cart([{"store_id": self.store1.id, "product_id": self.milk.id, "quantity": bad}])
                self.assertEqual(response.status_code, 400)

    def test_one_bad_line_saves_nothing(self):
        response = self.post_cart([
            {"store_id": self.store1.id, "product_id": self.milk.id, "quantity": 1},
            {"store_id": self.store1.id, "product_id": self.soap.id, "quantity": 1},
        ])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_must_be_logged_in(self):
        anonymous = APIClient()
        response = anonymous.post("/store/orders", {"items": []}, format="json")
        self.assertIn(response.status_code, (401, 403))

    def test_order_reduces_stock(self):
        responce = self.post_cart([
            {"store_id": self.store1.id, "product_id": self.milk.id, "quantity": 1}
        ])
        self.assertEqual(responce.status_code, 201)
        row = StoreProduct.objects.get(store=self.store1, product=self.milk)  
        self.assertEqual(row.stock, 9)

    def test_order_out_of_stock(self):
        responce = self.post_cart([
                    {"store_id": self.store1.id, "product_id": self.milk.id, "quantity": 11}
                ])
        self.assertEqual(responce.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

        row = StoreProduct.objects.get(store=self.store1, product=self.milk)
        self.assertEqual(row.stock, 10)

    def test_product_stores_returns_store_with_stock(self):
        response = self.client.get(f"/store/products/{self.milk.id}/stores")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["store_id"], self.store1.id)
        self.assertEqual(data[0]["stock"], 10)

    def test_product_stores_hides_zero_stock(self):
        row = StoreProduct.objects.get(store=self.store1, product=self.milk)
        row.stock = 0
        row.save()
        response = self.client.get(f"/store/products/{self.milk.id}/stores")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_product_stores_empty_for_unsold_product(self):
        eggs = Product.objects.create(product_name="Eggs", category="Groceries", price=5.00)
        response = self.client.get(f"/store/products/{eggs.id}/stores")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
                


class CancelOrderTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.customer = User.objects.create_user(username="nishant", password="pass12345")
        self.other_customer = User.objects.create_user(username="otheruser", password="pass12345")
        shopkeeper = User.objects.create_user(username="shopkeeper", password="pass12345")
        merchant = Merchant.objects.create(user=shopkeeper)

        self.store1 = Store.objects.create(owner=merchant, store_name="Sharma Kirana")
        self.order = Order.objects.create(user=self.customer, store=self.store1)

        self.client = APIClient()
        self.client.force_login(self.customer)

    def test_cancel_placed_order_returns_200(self):
        response = self.client.post(f"/store/orders/{self.order.id}/cancel")
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.CANCELLED)

    def test_cancel_delevery_order_400(self):
        self.order.status = Order.Status.DELIVERED
        self.order.save()
        response = self.client.post(f"/store/orders/{self.order.id}/cancel")
        self.assertEqual(response.status_code, 400)

    def test_cancel_someone_else_order_404(self):
        self.client.force_login(self.other_customer)
        response = self.client.post(f"/store/orders/{self.order.id}/cancel")
        self.assertEqual(response.status_code, 404)

    def test_cancel_nonexistent_order_returns_404(self):
        response = self.client.post("/store/orders/9999/cancel")
        self.assertEqual(response.status_code, 404)


        