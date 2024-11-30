
# API Endpoints for E-commerce Backend
## Sales Service

### API: Display Available Goods
- **Method:** GET
- **Endpoint:** `/sales/display-goods`
- **Response:**
  - **Success:** `200 OK`
  - **Example Response:**
    ```json
    [
      {"name": "Laptop", "price": 999.99},
      {"name": "Headphones", "price": 49.99}
    ]
    ```

### API: Get Goods Details
- **Method:** GET
- **Endpoint:** `/sales/goods/{good_id}`
- **Response:**
  - **Success:** `200 OK`
  - **Failure:** `404 Not Found` (e.g., good does not exist).
  - **Example Response:**
    ```json
    {
      "id": 1,
      "name": "Laptop",
      "category": "electronics",
      "price": 999.99,
      "description": "High-performance laptop",
      "count": 5
    }
    ```

### API: Process Sale
- **Method:** POST
- **Endpoint:** `/sales/sell`
- **Payload:**
  ```json
  {
    "username": "johndoe",
    "good_id": 1,
    "quantity": 2
  }
  ```
- **Response:**
  - **Success:** `200 OK`
    ```json
    {
      "message": "Purchase successful",
      "remaining_balance": 200.00
    }
    ```
  - **Failure (insufficient funds):**
    ```json
    {
      "error": "Insufficient funds"
    }
    ```
  - **Failure (insufficient stock):**
    ```json
    {
      "error": "Insufficient stock"
    }
    ```

### API: Get Historical Purchases
- **Method:** GET
- **Endpoint:** `/sales/history/{username}`
- **Response:**
  - **Success:** `200 OK`
  - **Failure:** `404 Not Found` (e.g., customer does not exist).
  - **Example Response:**
    ```json
    [
      {
        "good_name": "Laptop",
        "quantity": 2,
        "total_price": 1999.98,
        "sale_date": "2024-11-29T15:30:00"
      }
    ]
    ```