from unicodedata import category
from django.test import TestCase
from django.core.cache import cache
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Category, Product

# Create your tests here.


class ModelTestCase(TestCase):
    def setUp(self):
        self.category1 = Category.objects.create(
            name="Category Unit Test 1", description="Testing Category Model"
        )
        self.category2 = Category.objects.create(name="Category Unit Test 2")
        self.product1 = Product.objects.create(
            name="Product Unit Test 1",
            description="Testing Product Model",
            price=10.25,
            category=self.category1,
        )
        self.product2 = Product.objects.create(
            name="Product Unit Test 2", price=5, category=self.category2
        )

    def test_category_creation(self):
        self.assertEqual(self.category1.name, "Category Unit Test 1")
        self.assertEqual(self.category1.description, "Testing Category Model")
        self.assertEqual(self.category2.name, "Category Unit Test 2")
        self.assertIsNone(self.category2.description)

    def test_product_creation(self):
        self.assertEqual(self.product1.name, "Product Unit Test 1")
        self.assertEqual(self.product1.category.name, "Category Unit Test 1")
        self.assertEqual(self.product1.description, "Testing Product Model")
        self.assertEqual(self.product1.price, 10.25)
        self.assertEqual(self.product2.name, "Product Unit Test 2")
        self.assertEqual(self.product2.category.name, "Category Unit Test 2")
        self.assertIsNone(self.product2.description)
        self.assertEqual(self.product2.price, 5)


class CategoryApiTestCase(APITestCase):
    def setUp(self):
        self.cache_key = "store:categories"
        self.url = "/api/categories"
        self.data1 = {
            "name": "cat1",
            "description": "cat1"
        }
        self.data2 = {
            "name": "cat2",
            "description": "cat2 test using ID"
        }
        self.data3 = {
            "name": "cat3",
            "description": "test redis cache flow"
        }
        self.data4 = {
            "name": "cat4",
            "description": "test redis cache flow"
        }

    def test_post_category(self):
        post_response = self.client.post(self.url, self.data1, format="json")
        data = post_response.data["data"]
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["name"], self.data1["name"])
        self.assertEqual(data["description"], self.data1["description"])
    
    def test_get_all_category(self):
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
    
    def test_get_category_by_id(self):
        post_response = self.client.post(self.url, self.data2, format="json")
        id = post_response.data["data"]["id"]
        get_response = self.client.get(f"{self.url}/{id}")
        data = get_response.data["data"]
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["name"], self.data2["name"])
        self.assertEqual(data["description"], self.data2["description"])
    
    def test_put_category_by_id(self):
        temp_data = {"name": "insert category"}
        post_response = self.client.post(self.url, temp_data, format="json")
        id = post_response.data["data"]["id"]
        update_data = {
            "name": "update category",
            "description": "category updated"
        }
        put_response = self.client.put(f"{self.url}/{id}",update_data, format="json")
        data = put_response.data["data"]
        self.assertEqual(put_response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["name"], update_data["name"])
        self.assertEqual(data["description"], update_data["description"])
    
    def test_delete_category_by_id(self):
        temp_data = {"name": "delete category"}
        post_response = self.client.post(self.url, temp_data, format="json")
        id = post_response.data["data"]["id"]
        delete_response = self.client.delete(f"{self.url}/{id}")
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_category_redis_flow(self):
        id = None
        #Check cache after get
        self.assertIsNone(cache.get(self.cache_key))
        get_response = self.client.get(self.url)
        data = get_response.data["data"]
        self.assertIsNotNone(cache.get(self.cache_key))
        self.assertEqual(cache.get(self.cache_key), data)
        
        #Check cache after post
        cache.set(self.cache_key, 'test', 60*5)
        post_response = self.client.post(self.url, self.data3, format="json")
        id = post_response.data["data"]["id"]
        self.assertIsNone(cache.get(self.cache_key))
        
        #Check cache after update by id
        cache.set(self.cache_key, 'test', 60*5)
        self.client.put(f"{self.url}/{id}", self.data4, format="json")
        self.assertIsNone(cache.get(self.cache_key))
        
        #check cache after delete by id
        cache.set(self.cache_key, 'test', 60*5)
        self.client.delete(f"{self.url}/{id}")
        self.assertIsNone(cache.get(self.cache_key))
        
        