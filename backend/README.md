# Money Diary Backend

This is the backend service for the Money Diary application, built with FastAPI and Tortoise ORM.

## API Endpoints

The API provides RESTful endpoints for managing various resources in the Money Diary application.

### Base URL

All API endpoints are prefixed with `/api/v1`.

### Patterns API

Endpoints for managing identification patterns that help categorize transactions.

#### Create a Pattern

Creates a new pattern and associates it with a subcategory.

- **URL**: `/api/v1/patterns/`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "exp_name": "string",
    "subcategory_id": integer
  }
  ```
- **Response**: 
  - **Success Response**:
    - **Code**: 200
    - **Content**: 
    ```json
    {
      "id": integer,
      "exp_name": "string",
      "subcategory_id": integer,
      "message": "Pattern created successfully"
    }
    ```
  - **Error Responses**:
    - **Code**: 404
    - **Content**: `{ "detail": "Subcategory with ID {subcategory_id} not found" }`
    
    OR
    
    - **Code**: 400
    - **Content**: `{ "detail": "Pattern with expression '{exp_name}' already exists for this subcategory" }`
    
    OR
    
    - **Code**: 500
    - **Content**: `{ "detail": "Failed to create pattern: {error_message}" }`

**Example Request**:

```bash
# Using curl
curl -X POST http://localhost:8000/api/v1/patterns/ \
  -H "Content-Type: application/json" \
  -d '{"exp_name": "NETFLIX*", "subcategory_id": 5}'

# Using httpie
http POST http://localhost:8000/api/v1/patterns/ exp_name="NETFLIX*" subcategory_id=5
```

**Example Response**:

```json
{
  "id": 42,
  "exp_name": "NETFLIX*",
  "subcategory_id": 5,
  "message": "Pattern created successfully"
}
```

#### Delete a Pattern

Removes a pattern from the database.

- **URL**: `/api/v1/patterns/{pattern_id}`
- **Method**: `DELETE`
- **URL Parameters**:
  - `pattern_id`: The ID of the pattern to delete
- **Response**: 
  - **Success Response**:
    - **Code**: 200
    - **Content**: `{ "message": "Pattern with ID {pattern_id} deleted successfully" }`
  - **Error Responses**:
    - **Code**: 404
    - **Content**: `{ "detail": "Pattern with ID {pattern_id} not found" }`
    
    OR
    
    - **Code**: 500
    - **Content**: `{ "detail": "Failed to delete pattern: {error_message}" }`

**Example Request**:

```bash
# Using curl
curl -X DELETE http://localhost:8000/api/v1/patterns/123

# Using httpie
http DELETE http://localhost:8000/api/v1/patterns/123
```

**Example Response**:

```json
{
  "message": "Pattern with ID 123 deleted successfully"
}
```

## Running the Application

To start the backend server:

```bash
cd /path/to/moneydiary/backend
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000` and the interactive API documentation at `http://localhost:8000/docs`.
