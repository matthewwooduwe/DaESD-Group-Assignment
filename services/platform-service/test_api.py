import requests
import json

BASE_URL = "http://localhost:8002/api"

def test_api():
    print("Testing API...")

    # 1. Register
    print("\n1. Registering Producer...")
    import time
    username = f"testproducer_{int(time.time())}"
    register_data = {
        "username": username,
        "password": "testpassword",
        "role": "PRODUCER",
        "email": f"{username}@test.com"
    }
    response = requests.post(f"{BASE_URL}/auth/register/", data=register_data)
    if response.status_code == 201:
        print("Registration Successful")
    elif response.status_code == 400 and "username" in response.json() and "already exists" in str(response.json()):
         print("User already exists")
    else:
        print(f"Registration Failed: {response.status_code} - {response.text}")
        return

    # 2. Login
    print("\n2. Logging in...")
    login_data = {
        "username": username,
        "password": "testpassword"
    }
    response = requests.post(f"{BASE_URL}/auth/login/", data=login_data)
    if response.status_code == 200:
        token = response.json()['access']
        print(f"Login Successful. Token obtained.")
    else:
        print(f"Login Failed: {response.status_code} - {response.text}")
        return

    # 3. Create Product
    print("\n3. Creating Product...")
    headers = {"Authorization": f"Bearer {token}"}
    product_data = {
        "name": "Carrots",
        "description": "they r orange :D",
        "price": "0.50",
        "category": "VEGETABLES",
        "stock_quantity": 100,
        "allergen_info": "None"
    }
    response = requests.post(f"{BASE_URL}/products/", data=product_data, headers=headers)
    product_data_response = {}
    if response.status_code == 201:
        print("Product Created Successfully")
        product_data_response = response.json()
        print(product_data_response)
    else:
        print(f"Product Creation Failed: {response.status_code} - {response.text}")

    # 4. List Products
    print("\n4. Listing Products...")
    response = requests.get(f"{BASE_URL}/products/")
    if response.status_code == 200:
        products = response.json()
        print(f"Retrieved {len(products)} products")
        for p in products:
            print(f" - {p['name']} (${p['price']}) by {p['producer_username']}")
    else:
        print(f"List Failed: {response.status_code} - {response.text}")

    # 5. Cleanup (Delete Product)
    print("\n5. Cleaning up (Deleting Product)...")
    if 'id' in product_data_response: # Ensure we have an ID from step 3
        product_id = product_data_response['id']
        response = requests.delete(f"{BASE_URL}/products/{product_id}/", headers=headers)
        if response.status_code == 204:
            print("Product Deleted Successfully")
        else:
            print(f"Delete Failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_api()
