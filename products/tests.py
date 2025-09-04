from django.test import TestCase, Client
from django.urls import reverse
from .models import Product, Category
from decimal import Decimal


class ProductCartTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.cat = Category.objects.create(name="Cat")
		self.product = Product.objects.create(category=self.cat, name="Test", price=Decimal('10.00'), is_active=True, slug="test")

	def test_add_to_cart(self):
		url = reverse('add_to_cart')
		resp = self.client.post(url, {'product_id': self.product.pk, 'qty': 2})
		self.assertEqual(resp.status_code, 200)
		data = resp.json()
		self.assertTrue(data['ok'])
		self.assertEqual(data['count'], 2)

	def test_cart_view_renders(self):
		self.client.post(reverse('add_to_cart'), {'product_id': self.product.pk, 'qty': 1})
		resp = self.client.get(reverse('cart'))
		self.assertContains(resp, "Test")

	def test_update_cart_remove(self):
		self.client.post(reverse('add_to_cart'), {'product_id': self.product.pk, 'qty': 1})
		key = f"P:{self.product.pk}"
		resp = self.client.post(reverse('update_cart_item'), {'product_id': key, 'action': 'remove'})
		self.assertEqual(resp.status_code, 200)
		self.assertTrue(resp.json()['removed'])
