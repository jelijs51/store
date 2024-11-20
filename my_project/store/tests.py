from unicodedata import category
from django.test import TestCase
from django.core.cache import cache
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Category, Product

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
            "description": "cat2"
        }
        self.data3 = {
            "name": "cat3",
            "description": "cat3"
        }
    
    def tearDown(self):
        cache.clear()

    def test_post_category(self):
        post_response = self.client.post(self.url, self.data1, format="json")
        data = post_response.data["data"]
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["name"], self.data1["name"])
        self.assertEqual(data["description"], self.data1["description"])
        
        # check unique
        post_response = self.client.post(self.url, self.data1, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_all_category(self):
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
    
    def test_get_category_by_id(self):
        post_response = self.client.post(self.url, self.data1, format="json")
        id = post_response.data["data"]["id"]
        get_response = self.client.get(f"{self.url}/{id}")
        data = get_response.data["data"]
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["name"], self.data1["name"])
        self.assertEqual(data["description"], self.data1["description"])
    
    def test_put_category_by_id(self):
        post_response = self.client.post(self.url, self.data1, format="json")
        id = post_response.data["data"]["id"]
        # exist id
        put_response = self.client.put(f"{self.url}/{id}",self.data2, format="json")
        data = put_response.data["data"]
        self.assertEqual(put_response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["name"], self.data2["name"])
        self.assertEqual(data["description"], self.data2["description"])
        
        # id not exist
        put_response = self.client.put(f"{self.url}/999",self.data2, format="json")
        self.assertEqual(put_response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_category_by_id(self):
        post_response = self.client.post(self.url, self.data1, format="json")
        id = post_response.data["data"]["id"]
        delete_response = self.client.delete(f"{self.url}/{id}")
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        
        # id not exist
        delete_response = self.client.delete(f"{self.url}/999")
        self.assertEqual(delete_response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_category_redis_flow(self):
        # Init data
        self.client.post(self.url,{"name":"test_data"})
        
        # Check cache after get
        self.assertIsNone(cache.get(self.cache_key))
        get_response = self.client.get(self.url)
        data = get_response.data["data"]
        self.assertIsNotNone(cache.get(self.cache_key))
        self.assertEqual(cache.get(self.cache_key), data)
        
        # Check cache after post
        cache.set(self.cache_key, "test", 60*5)
        post_response = self.client.post(self.url, self.data1, format="json")
        id = post_response.data["data"]["id"]
        self.assertIsNone(cache.get(self.cache_key))
        
        # Check cache after update by id
        cache.set(self.cache_key, "test", 60*5)
        self.client.put(f"{self.url}/{id}", self.data3, format="json")
        self.assertIsNone(cache.get(self.cache_key))
        
        # check cache after delete by id
        cache.set(self.cache_key, "test", 60*5)
        self.client.delete(f"{self.url}/{id}")
        self.assertIsNone(cache.get(self.cache_key))
        
class ProductApiTest(APITestCase):
    
    def setUp(self):
        self.cache_key = "store:products"
        self.url = "/api/products"
        post_response1 = self.client.post("/api/categories", {"name": "cat1", "description": "cat1"}, format="json")
        post_response2 = self.client.post("/api/categories", {"name": "cat2"}, format="json")
        self.catid1 = post_response1.data["data"]["id"]
        self.catid2 = post_response2.data["data"]["id"]
        self.data1 = {
            "name": "test1",
            "description": "test",
            "price": "10.00",
            "category": self.catid1
        }
        self.data2 = {
            "name": "test2",
            "price": "25",
            "category": self.catid2
        }
        self.data3 = {
            "name": "test3",
            "price": "50",
            "category": self.catid1
        }
    
    def tearDown(self):
        cache.clear()
    
    def test_post_product(self):
        post_response = self.client.post(self.url, self.data1, format="json")
        data = post_response.data["data"]
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["name"], self.data1["name"])
        self.assertEqual(data["description"], self.data1["description"])
        self.assertEqual(float(data["price"]), float(self.data1["price"]))
        self.assertEqual(data["category"], self.data1["category"])

    def test_get_all_product(self):
        self.client.post(self.url, self.data1, format="json")
        self.client.post(self.url, self.data2, format="json")
        self.client.post(self.url, self.data3, format="json")
        
        # Test Get All data
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_response.data["data"]), 3)
        
        # Test GET by category 1 (cat1)
        get_response = self.client.get(f"{self.url}?category_name=cat1")
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_response.data["data"]), 2)
        
        # Test GET by unknown category name
        get_response = self.client.get(f"{self.url}?category_name=asd")
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

        # Test: Filter by price_min (price >= 20)
        get_response = self.client.get(f"{self.url}?price_min=20")
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_response.data["data"]), 2) 

        # Test: Filter by price_max (price <= 25)
        get_response = self.client.get(f"{self.url}?price_max=25")
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_response.data["data"]), 2)

        # Test: Filter by price_min and price_max (20 <= price <= 30)
        get_response = self.client.get(f"{self.url}?price_min=20&price_max=30")
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_response.data["data"]), 1)

        # Test: Invalid price filter 
        get_response = self.client.get(f"{self.url}?price_min=abc")
        self.assertEqual(get_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(get_response.data["message"], "Invalid price filter values")
    
    def test_get_product_by_id(self):
        post_response = self.client.post(self.url, self.data1, format="json")
        id = post_response.data["data"]["id"]
        get_response = self.client.get(f"{self.url}/{id}")
        data = get_response.data["data"]
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["name"], self.data1["name"])
        self.assertEqual(data["description"], self.data1["description"])
        self.assertEqual(float(data["price"]), float(self.data1["price"]))
        self.assertEqual(data["category"], self.data1["category"])
    
    def test_put_product_by_id(self):
        post_response = self.client.post(self.url, self.data1, format="json")
        id = post_response.data["data"]["id"]
        put_response = self.client.put(f"{self.url}/{id}", self.data2, format="json")
        data = put_response.data["data"]
        self.assertEqual(put_response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["name"], self.data2["name"])
        self.assertEqual(float(data["price"]), float(self.data2["price"]))
        self.assertEqual(data["description"], self.data1["description"])
        self.assertEqual(data["category"], self.data2["category"])
        
    def test_delete_product_by_id(self):
        post_response = self.client.post(self.url, self.data1, format="json")
        id = post_response.data["data"]["id"]
        delete_response = self.client.delete(f"{self.url}/{id}")
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_product_redis_flow(self):
        # Init data
        self.client.post(self.url, self.data1, format="json")
        
        # Check cache after get
        self.assertIsNone(cache.get(self.cache_key))
        get_response = self.client.get(self.url)
        data = get_response.data["data"]
        self.assertIsNotNone(cache.get(self.cache_key))
        self.assertEqual(cache.get(self.cache_key), data)
        
        # Check cache after post
        cache.set(self.cache_key, "test", 60*5)
        post_response = self.client.post(self.url, self.data2, format="json")
        id = post_response.data["data"]["id"]
        self.assertIsNone(cache.get(self.cache_key))
        
        # Check cache after update by id
        cache.set(self.cache_key, "test", 60*5)
        self.client.put(f"{self.url}/{id}", self.data3, format="json")
        self.assertIsNone(cache.get(self.cache_key))
        
        # check cache after delete by id
        cache.set(self.cache_key, "test", 60*5)
        self.client.delete(f"{self.url}/{id}")
        self.assertIsNone(cache.get(self.cache_key))
        
        