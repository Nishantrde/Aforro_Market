from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import Merchant
from .models import Order, OrderItem, Product, Store, StoreProduct

from django.test import SimpleTestCase
from .views import can_move

from django.core.cache import cache
from unittest import mock

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

        self.milk = Product.objects.create(product_name="Milk", category="Groceries", price=2.50)
        self.stock_row = StoreProduct.objects.create(store=self.store1, product=self.milk, stock=10)
        OrderItem.objects.create(order=self.order, product=self.milk, quantity=3, price=Decimal("2.50"))
        
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

    def test_cancel_restores_stock(self):
        response = self.client.post(f"/store/orders/{self.order.id}/cancel")
        self.assertEqual(response.status_code, 200)
        self.stock_row.refresh_from_db()
        self.assertEqual(self.stock_row.stock, 13)

    def test_cancel_twice_restores_stock_only_once(self):
        first = self.client.post(f"/store/orders/{self.order.id}/cancel")
        second = self.client.post(f"/store/orders/{self.order.id}/cancel")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 400)
        self.stock_row.refresh_from_db()
        self.assertEqual(self.stock_row.stock, 13)   # not 16

    def test_cancel_delivered_order_does_not_touch_stock(self):
        self.order.status = Order.Status.DELIVERED
        self.order.save()
        response = self.client.post(f"/store/orders/{self.order.id}/cancel")
        self.assertEqual(response.status_code, 400)
        self.stock_row.refresh_from_db()
        self.assertEqual(self.stock_row.stock, 10)

class MyOrdersTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.customer = User.objects.create_user(username="nishant", password="pass12345")
        self.other_customer = User.objects.create_user(username="otheruser", password="pass12345")
        shopkeeper = User.objects.create_user(username="shopkeeper", password="pass12345")
        merchant = Merchant.objects.create(user=shopkeeper)

        self.store1 = Store.objects.create(owner=merchant, store_name="Sharma Kirana")
        self.milk = Product.objects.create(product_name="Milk", category="Groceries", price=2.50)
        self.bread = Product.objects.create(product_name="Bread", category="Groceries", price=3.20)

        # one order: 2 milk + 1 bread = 5.00 + 3.20 = 8.20
        self.order = Order.objects.create(user=self.customer, store=self.store1)
        OrderItem.objects.create(order=self.order, product=self.milk, quantity=2, price=Decimal("2.50"))
        OrderItem.objects.create(order=self.order, product=self.bread, quantity=1, price=Decimal("3.20"))

        self.client = APIClient()
        self.client.force_login(self.customer)

    def test_my_orders_returns_own_order_with_total(self):
        response = self.client.get("/store/orders/list")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.order.id)
        self.assertEqual(data[0]["store"], "Sharma Kirana")
        self.assertEqual(data[0]["status"], "PLACED")
        self.assertEqual(Decimal(data[0]["total"]), Decimal("8.20"))

    def test_my_orders_lists_item_names_and_quantities(self):
        data = self.client.get("/store/orders/list").json()
        items = {i["name"]: i["quantity"] for i in data[0]["items"]}
        self.assertEqual(items, {"Milk": 2, "Bread": 1})

    def test_other_customer_sees_no_orders(self):
        self.client.force_login(self.other_customer)
        response = self.client.get("/store/orders/list")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_my_orders_requires_login(self):
        anonymous = APIClient()
        response = anonymous.get("/store/orders/list")
        self.assertIn(response.status_code, (401, 403))

class CanMoveTests(SimpleTestCase):

    def test_legal_moves(self):
        self.assertTrue(can_move("PLACED", "CONFIRMED"))
        self.assertTrue(can_move("CONFIRMED", "PACKED"))
        self.assertTrue(can_move("PACKED", "OUT_FOR_DELIVERY"))
        self.assertTrue(can_move("OUT_FOR_DELIVERY", "DELIVERED"))

    def test_cannot_skip_steps(self):
        self.assertFalse(can_move("PLACED", "DELIVERED"))
        self.assertFalse(can_move("PLACED", "PACKED"))

    def test_cannot_go_backwards(self):
        self.assertFalse(can_move("PACKED", "PLACED"))

    def test_final_states_cannot_move(self):
        self.assertFalse(can_move("DELIVERED", "PLACED"))
        self.assertFalse(can_move("CANCELLED", "CONFIRMED"))

class UpdateOrderStatusTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.customer = User.objects.create_user(username="nishant", password="pass12345")
        self.owner = User.objects.create_user(username="shopkeeper", password="pass12345")
        self.other_owner = User.objects.create_user(username="shopkeeper2", password="pass12345")
        merchant = Merchant.objects.create(user=self.owner)
        Merchant.objects.create(user=self.other_owner)

        self.store1 = Store.objects.create(owner=merchant, store_name="Sharma Kirana")
        self.order = Order.objects.create(user=self.customer, store=self.store1)

        self.client = APIClient()
        self.client.force_login(self.owner)

    def post_status(self, new_status):
        return self.client.post(
            f"/store/orders/{self.order.id}/status", {"status": new_status}, format="json"
        )

    def test_owner_can_confirm_order(self):
        response = self.post_status("CONFIRMED")
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "CONFIRMED")

    def test_cannot_skip_to_delivered(self):
        response = self.post_status("DELIVERED")
        self.assertEqual(response.status_code, 400)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "PLACED")

    def test_cannot_set_cancelled_here(self):
        response = self.post_status("CANCELLED")
        self.assertEqual(response.status_code, 400)

    def test_other_shopkeeper_gets_404(self):
        self.client.force_login(self.other_owner)
        response = self.post_status("CONFIRMED")
        self.assertEqual(response.status_code, 404)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "PLACED")

    def test_customer_gets_404(self):
        self.client.force_login(self.customer)
        response = self.post_status("CONFIRMED")
        self.assertEqual(response.status_code, 404)

class MerchantOrdersTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.customer = User.objects.create_user(username="nishant", password="pass12345")
        self.owner = User.objects.create_user(username="shopkeeper", password="pass12345")
        self.other_owner = User.objects.create_user(username="shopkeeper2", password="pass12345")
        merchant = Merchant.objects.create(user=self.owner)
        Merchant.objects.create(user=self.other_owner)

        self.store1 = Store.objects.create(owner=merchant, store_name="Sharma Kirana")
        self.order = Order.objects.create(user=self.customer, store=self.store1)

        self.client = APIClient()
        self.client.force_login(self.owner)

    def test_owner_sees_order_for_his_store(self):
        response = self.client.get("/store/merchant/orders")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.order.id)
        self.assertEqual(data[0]["customer"], "nishant")

    def test_other_shopkeeper_sees_nothing(self):
        self.client.force_login(self.other_owner)
        response = self.client.get("/store/merchant/orders")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_customer_sees_nothing(self):
        self.client.force_login(self.customer)
        response = self.client.get("/store/merchant/orders")
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(response.json(), [])

    def test_requires_login(self):
        anonymous = APIClient()
        response = anonymous.get("/store/merchant/orders")
        self.assertIn(response.status_code, (401, 403))

class ProductCacheTests(TestCase):
    def setUp(self):
        cache.clear()
        User = get_user_model()
        self.milk = Product.objects.create(product_name = "Milk", category="Groceries", price=2.50)
        shopkeeper = User.objects.create_user(username="shopkeeper", password="pass12345")
        merchant = Merchant.objects.create(user=shopkeeper)
        self.store1 = Store.objects.create(owner=merchant, store_name="Sharma Kirana")
        self.stock_row = StoreProduct.objects.create(store = self.store1, product = self.milk, stock = 10)
        self.client = APIClient()

    def test_second_call_dose_not_hit_database(self):
        self.client.get("/store/products")
        with self.assertNumQueries(0):
            responce = self.client.get("/store/products")
        self.assertEqual(responce.status_code, 200)

    def test_cached_list_is_stale_until_cache_clears(self):
        self.client.get('/store/products')
        self.milk.product_name = "Oat Milk"
        self.milk.save()
        responce = self.client.get('/store/products')
        self.assertEqual(responce.json()[0]["product_name"], "Milk")
        cache.clear()
        responce = self.client.get('/store/products')
        self.assertEqual(responce.json()[0]["product_name"], "Oat Milk")

    def test_stock_is_never_cached(self):
        url = f'/store/products/{self.milk.id}/stores'
        responce = self.client.get(url)
        self.assertEqual(responce.json()[0]["stock"], 10)

        self.stock_row.stock = 4
        self.stock_row.save()

        responce =  self.client.get(f'/store/products/{self.milk.id}/stores')
        self.assertEqual(responce.json()[0]["stock"], 4)

    def test_products_still_works_well_when_cache_get_fails(self):
        with mock.patch("stores.views.cache.get", side_effect = Exception("redis down")):
            responce = self.client.get("/store/products")
        self.assertEqual(responce.status_code, 200)
        self.assertEqual(responce.json()[0]["product_name"], "Milk")

    def test_products_still_works_well_when_cache_set_fails(self):
            with mock.patch("stores.views.cache.set", side_effect = Exception("redis down")):
                responce = self.client.get("/store/products")
            self.assertEqual(responce.status_code, 200)
            self.assertEqual(responce.json()[0]["product_name"], "Milk")
    
                    
        


