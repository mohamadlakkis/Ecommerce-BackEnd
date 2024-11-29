
# API Endpoints for E-commerce Backend

## Customers Service

### API: Customer Registration
- **Method:** POST
- **Endpoint:** `/customers/register`
- **Payload:**
  ```json
  {
    "full_name": "John Doe",
    "username": "johndoe",
    "password": "securepassword",
    "age": 19,
    "address": "Beirut",
    "gender": "Male",
    "marital_status": "Single"
  }
  ```
- **Response:**
  - **Success:** `201 Created`
  - **Failure:** `400 Bad Request` (e.g., username is not unique)

### API: Delete Customer
- **Method:** DELETE
- **Endpoint:** `/customers/{username}`
- **Response:**
  - **Success:** `200 OK`
  - **Failure:** `404 Not Found` (e.g., username does not exist)

### API: Update Customer Information
- **Method:** PATCH
- **Endpoint:** `/customers/{username}`
- **Payload Example:**
  ```json
  {
    "age": 35,
    "address": "Saida"
  }
  ```
- **Response:**
  - **Success:** `200 OK`
  - **Failure:** `404 Not Found` (e.g., username does not exist)

### API: Get All Customers
- **Method:** GET
- **Endpoint:** `/customers`
- **Response:**
  - **Success:** `200 OK`
  - **Example Response:**
    ```json
    [
      {
        "id": 1,
        "full_name": "John Doe",
        "username": "johndoe",
        "age": 19,
        "address": "beirut",
        "gender": "Male",
        "marital_status": "Single",
        "wallet_balance": 0.0
      }
    ]
    ```

### API: Get Customer by Username
- **Method:** GET
- **Endpoint:** `/customers/{username}`
- **Response:**
  - **Success:** `200 OK`
  - **Failure:** `404 Not Found` (e.g., username does not exist)
  - **Example Response:**
    ```json
    {
      "id": 1,
      "full_name": "John Doe",
      "username": "johndoe",
      "age": 19,
      "address": "beirut",
      "gender": "Male",
      "marital_status": "Single",
      "wallet_balance": 0.0
    }
    ```

### API: Charge Customer Wallet
- **Method:** PUT
- **Endpoint:** `/customers/{username}/charge`
- **Payload:**
  ```json
  {
    "amount": 50.00
  }
  ```
- **Response:**
  - **Success:** `200 OK`
  - **Failure:** `404 Not Found` (e.g., username does not exist)
  - **Example Response:**
    ```json
    {
      "username": "johndoe",
      "wallet_balance": 50.00
    }
    ```

### API: Deduct Money from Wallet
- **Method:** PUT
- **Endpoint:** `/customers/{username}/deduct`
- **Payload:**
  ```json
  {
    "amount": 30.00
  }
  ```
- **Response:**
  - **Success:** `200 OK`
  - **Failure:** `400 Bad Request` (e.g., insufficient funds)
  - **Example Response:**
    ```json
    {
      "username": "johndoe",
      "wallet_balance": 20.00
    }
    ```

## Inventory Service

### API: Add Goods
- **Method:** POST
- **Endpoint:** `/inventory/add`
- **Payload:**
  ```json
  {
    "name": "Laptop",
    "category": "electronics",
    "price": 999.99,
    "description": "A high-performance laptop",
    "count": 10
  }
  ```
- **Response:**
  - **Success:** `201 Created`
  - **Failure:** `400 Bad Request` (e.g., missing fields).

### API: Deduct Goods
- **Method:** PUT
- **Endpoint:** `/inventory/{id}/deduct`
- **Payload:**
  ```json
  {
    "count": 2
  }
  ```
- **Response:**
  - **Success:** `200 OK`
  - **Failure:** `400 Bad Request` (e.g., insufficient stock or invalid item).

### API: Update Goods
- **Method:** PATCH
- **Endpoint:** `/inventory/{id}/update`
- **Payload Example:**
  ```json
  {
    "price": 500.99,
    "description": "Discounted high-performance laptop"
  }
  ```
- **Response:**
  - **Success:** `200 OK`
  - **Failure:** `404 Not Found` (e.g., item does not exist).