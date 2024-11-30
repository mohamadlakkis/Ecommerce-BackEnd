
# API Endpoints for E-commerce Backend
## Reviews Service

### API: Submit Review
- **Method:** POST
- **Endpoint:** `/reviews/submit`
- **Payload:**
  ```json
  {
    "username": "johndoe",
    "product_id": 1,
    "rating": 5,
    "comment": "Excellent product!"
  }
  ```
- **Response:**
  - **Success:** `201 Created`
    ```json
    {
      "message": "Review submitted successfully"
    }
    ```
  - **Failure (Missing fields):** `400 Bad Request`
    ```json
    {
      "error": "Missing fields"
    }
    ```

### API: Update Review
- **Method:** PATCH
- **Endpoint:** `/reviews/{review_id}/update`
- **Payload:**
  ```json
  {
    "rating": 4,
    "comment": "Updated feedback: Good, but could be better."
  }
  ```
- **Response:**
  - **Success:** `200 OK`
    ```json
    {
      "message": "Review updated successfully"
    }
    ```
  - **Failure:** `404 Not Found`
    ```json
    {
      "error": "Review not found"
    }
    ```

### API: Delete Review
- **Method:** DELETE
- **Endpoint:** `/reviews/{review_id}/delete`
- **Response:**
  - **Success:** `200 OK`
    ```json
    {
      "message": "Review deleted successfully"
    }
    ```
  - **Failure:** `404 Not Found`
    ```json
    {
      "error": "Review not found"
    }
    ```

### API: Get Product Reviews
- **Method:** GET
- **Endpoint:** `/reviews/product/{product_id}`
- **Response:**
  - **Success:** `200 OK`
    ```json
    [
      {
        "username": "johndoe",
        "rating": 5,
        "comment": "Excellent product!",
        "review_date": "2024-11-29T12:00:00"
      }
    ]
    ```
  - **Failure (No reviews):** `200 OK` (empty array)
    ```json
    []
    ```

### API: Get Customer Reviews
- **Method:** GET
- **Endpoint:** `/reviews/customer/{username}`
- **Response:**
  - **Success:** `200 OK`
    ```json
    [
      {
        "product_name": "Laptop",
        "rating": 5,
        "comment": "Excellent performance",
        "review_date": "2024-11-29T12:00:00"
      }
    ]
    ```
  - **Failure:** `404 Not Found`
    ```json
    {
      "error": "Customer not found"
    }
    ```

### API: Moderate Review
- **Method:** PATCH
- **Endpoint:** `/reviews/{review_id}/moderate`
- **Payload:**
  ```json
  {
    "status": "approved"
  }
  ```
- **Response:**
  - **Success:** `200 OK`
    ```json
    {
      "message": "Review status updated to approved"
    }
    ```
  - **Failure (Invalid status):** `400 Bad Request`
    ```json
    {
      "error": "Invalid status"
    }
    ```
  - **Failure (Review not found):** `404 Not Found`
    ```json
    {
      "error": "Review not found"
    }
    ```

### API: Get Review Details
- **Method:** GET
- **Endpoint:** `/reviews/{review_id}`
- **Response:**
  - **Success:** `200 OK`
    ```json
    {
      "username": "johndoe",
      "product_name": "Laptop",
      "rating": 5,
      "comment": "Excellent performance",
      "status": "approved",
      "review_date": "2024-11-29T12:00:00"
    }
    ```
  - **Failure:** `404 Not Found`
    ```json
    {
      "error": "Review not found"
    }
    ```