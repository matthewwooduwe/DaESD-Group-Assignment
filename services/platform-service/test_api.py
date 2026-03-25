import requests
import time
import sys

BASE_URL = "http://localhost:8002/api"

class APITester:
    def __init__(self):
        self.producer_token = None
        self.customer_token = None
        self.producer_data = None
        self.customer_data = None
        
        # Track created resources for cleanup
        self.created_reviews = [] # list of (id, token)
        self.created_orders = [] # list of (id, token)
        self.created_products = [] # list of (id, token)
        self.created_categories = [] # list of (id, token)
        self.created_recipes = [] # list of (id, token)
        self.created_farm_stories = [] # list of (id, token)
        self.created_users = [] # list of (username, token)

    def log(self, msg, success=True):
        prefix = "[SUCCESS]" if success else "[FAILED]"
        print(f"{prefix} {msg}")

    def run(self):
        try:
            print("Starting API Tests...")
            self.test_producer_registration()
            self.test_producer_login()
            self.test_category_creation()
            self.test_product_creation()
            self.test_recipe_creation()
            self.test_farm_story_creation()
            self.test_customer_registration()
            self.test_customer_login()
            self.test_order_creation()
            self.test_review_creation()
            print("\nAll tests passed successfully!")
        except Exception as e:
            self.log(f"Test Execution Halt: {e}", success=False)
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()

    def test_producer_registration(self):
        print("\n1. Registering Producer...")
        username = f"prod_{int(time.time())}"
        self.producer_data = {
            "username": username,
            "password": "testpassword",
            "role": "PRODUCER",
            "email": f"{username}@test.com",
            "producer_profile": {
                "business_name": f"{username} Farm",
                "business_address": "123 Farm Lane",
                "postcode": "BS1 1AA",
                "bio": "Fresh produce"
            }
        }
        response = requests.post(f"{BASE_URL}/auth/register/", json=self.producer_data)
        if response.status_code == 201:
            self.log("Producer Registered")
        else:
            raise Exception(f"Register Failed: {response.text}")

    def test_producer_login(self):
        print("\n2. Logging in Producer...")
        login_data = {"username": self.producer_data['username'], "password": "testpassword"}
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        if response.status_code == 200:
            self.producer_token = response.json()['access']
            self.created_users.append((self.producer_data['username'], self.producer_token))
            self.log("Producer Logged In")
        else:
            raise Exception(f"Login Failed: {response.text}")

    def test_category_creation(self):
        print("\n3. Creating Category...")
        headers = {"Authorization": f"Bearer {self.producer_token}"}
        cat_name = f"Veg_{int(time.time())}"
        category_data = {"name": cat_name}
        response = requests.post(f"{BASE_URL}/products/categories/", json=category_data, headers=headers)
        if response.status_code == 201:
            self.log("Category Created")
            self.created_categories.append((response.json()['id'], self.producer_token))
            self.current_category_name = cat_name
        elif response.status_code == 400 and "already exists" in response.text:
             self.log("Category already exists")
             self.current_category_name = cat_name
        else:
            raise Exception(f"Category Create Failed: {response.text}")

    def test_product_creation(self):
        print("\n4. Creating Product...")
        headers = {"Authorization": f"Bearer {self.producer_token}"}
        
        product_data = {
            "name": f"Carrot_{int(time.time())}",
            "description": "Crunchy",
            "price": "1.50",
            "category": self.current_category_name,
            "stock_quantity": 100,
            "unit": "kg",
            "is_organic": True
        }
        
        response = requests.post(f"{BASE_URL}/products/", json=product_data, headers=headers)
        if response.status_code == 201:
            self.log("Product Created")
            self.created_products.append((response.json()['id'], self.producer_token))
            self.current_product_id = response.json()['id']
        else:
             raise Exception(f"Product Create Failed: {response.text}")

    def test_recipe_creation(self):
        print("\n4a. Creating Recipe...")
        headers = {"Authorization": f"Bearer {self.producer_token}"}
        recipe_data = {
            "title": f"Recipe_{int(time.time())}",
            "description": "Tasty",
            "ingredients": "Carrots",
            "instructions": "Cook it",
            "season_tag": "Summer",
            "products": [self.current_product_id]
        }
        response = requests.post(f"{BASE_URL}/products/recipes/", json=recipe_data, headers=headers)
        if response.status_code == 201:
            self.log("Recipe Created")
            self.created_recipes.append((response.json()['id'], self.producer_token))
        else:
             raise Exception(f"Recipe Create Failed: {response.text}")

    def test_farm_story_creation(self):
        print("\n4b. Creating Farm Story...")
        headers = {"Authorization": f"Bearer {self.producer_token}"}
        story_data = {
            "title": f"Story_{int(time.time())}",
            "content": "A story about farm."
        }
        response = requests.post(f"{BASE_URL}/products/farm-stories/", json=story_data, headers=headers)
        if response.status_code == 201:
            self.log("Farm Story Created")
            self.created_farm_stories.append((response.json()['id'], self.producer_token))
        else:
             raise Exception(f"Farm Story Create Failed: {response.text}")

    def test_customer_registration(self):
        print("\n5. Registering Customer...")
        username = f"cust_{int(time.time())}"
        self.customer_data = {
            "username": username,
            "password": "testpassword",
            "role": "CUSTOMER",
            "email": f"{username}@test.com",
            "customer_profile": {
                "full_name": "Jane Doe",
                "delivery_address": "456 City Rd",
                "postcode": "BS2 2BB"
            }
        }
        response = requests.post(f"{BASE_URL}/auth/register/", json=self.customer_data)
        if response.status_code == 201:
            self.log("Customer Registered")
        else:
            raise Exception(f"Register Failed: {response.text}")

    def test_customer_login(self):
        print("\n6. Logging in Customer...")
        login_data = {"username": self.customer_data['username'], "password": "testpassword"}
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        if response.status_code == 200:
            self.customer_token = response.json()['access']
            self.created_users.append((self.customer_data['username'], self.customer_token))
            self.log("Customer Logged In")
        else:
            raise Exception(f"Login Failed: {response.text}")

    def test_order_creation(self):
        print("\n7. Creating Order...")
        headers = {"Authorization": f"Bearer {self.customer_token}"}
        order_data = {
            "item_ids": [{"product_id": self.current_product_id, "quantity": 5}]
        }
        response = requests.post(f"{BASE_URL}/orders/", json=order_data, headers=headers)
        if response.status_code == 201:
            self.log("Order Created")
            self.current_order_id = response.json()['id']
            self.created_orders.append((self.current_order_id, self.customer_token))
        else:
             raise Exception(f"Order Create Failed: {response.text}")

    def test_review_creation(self):
        print("\n8. Adding Review...")
        headers = {"Authorization": f"Bearer {self.customer_token}"}
        review_data = {
            "product": self.current_product_id,
            "order": self.current_order_id,
            "rating": 5,
            "comment": "Great!"
        }
        response = requests.post(f"{BASE_URL}/reviews/", json=review_data, headers=headers)
        if response.status_code == 201:
            self.log("Review Added")
            self.created_reviews.append((response.json()['id'], self.customer_token))
        else:
             raise Exception(f"Review Failed: {response.text}")

    def cleanup(self):
        print("\n--- Cleaning up resources ---")
        
        # Reviews
        for rid, token in self.created_reviews:
            r = requests.delete(f"{BASE_URL}/reviews/{rid}/", headers={"Authorization": f"Bearer {token}"})
            print(f"Deleted Review {rid}: {r.status_code}")
            
        # Orders
        for oid, token in self.created_orders:
            r = requests.delete(f"{BASE_URL}/orders/{oid}/", headers={"Authorization": f"Bearer {token}"})
            print(f"Deleted Order {oid}: {r.status_code}")
            
        # Products
        for pid, token in self.created_products:
            r = requests.delete(f"{BASE_URL}/products/{pid}/", headers={"Authorization": f"Bearer {token}"})
            print(f"Deleted Product {pid}: {r.status_code}")
            
        # Categories
        for cid, token in self.created_categories:
            r = requests.delete(f"{BASE_URL}/products/categories/{cid}/", headers={"Authorization": f"Bearer {token}"})
            print(f"Deleted Category {cid}: {r.status_code}")
            
        # Recipes
        for rid, token in self.created_recipes:
            r = requests.delete(f"{BASE_URL}/products/recipes/{rid}/", headers={"Authorization": f"Bearer {token}"})
            print(f"Deleted Recipe {rid}: {r.status_code}")
            
        # Farm Stories
        for fid, token in self.created_farm_stories:
            r = requests.delete(f"{BASE_URL}/products/farm-stories/{fid}/", headers={"Authorization": f"Bearer {token}"})
            print(f"Deleted Farm Story {fid}: {r.status_code}")
            
        # Users (Self deletion)
        # We need to cleanup created users tokens first? No, we use them.
        for username, token in self.created_users:
            r = requests.delete(f"{BASE_URL}/auth/me/", headers={"Authorization": f"Bearer {token}"})
            print(f"Deleted User {username}: {r.status_code}")
            
        print("Cleanup Complete.")

if __name__ == "__main__":
    tester = APITester()
    tester.run()
