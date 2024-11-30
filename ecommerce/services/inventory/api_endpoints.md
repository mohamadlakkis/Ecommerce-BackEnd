# API Endpoints for E-commerce Backend
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