# Todo REST API

A simple, fast REST API for managing todo items built with **FastAPI**.

## Features

- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ✅ RESTful endpoint design
- ✅ In-memory storage (no database required)
- ✅ Automatic API documentation with Swagger UI
- ✅ Comprehensive test suite with pytest

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone or navigate to the project directory:
   ```bash
   cd todo_rest_api
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

Start the development server with automatic reload:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

**Interactive API Documentation:**
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Running Tests

Run the pytest test suite:

```bash
pytest
```

For verbose output:
```bash
pytest -v
```

For coverage report:
```bash
pytest --cov=main
```

## API Endpoints

### Create a Todo
**POST** `/todos`

Request body:
```json
{
  "title": "Buy groceries"
}
```

Response (201 Created):
```json
{
  "id": 1,
  "title": "Buy groceries",
  "completed": false,
  "created_at": "2024-01-15T10:30:00.123456"
}
```

### List All Todos
**GET** `/todos`

Response (200 OK):
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "completed": false,
    "created_at": "2024-01-15T10:30:00.123456"
  },
  {
    "id": 2,
    "title": "Do laundry",
    "completed": true,
    "created_at": "2024-01-15T10:31:00.654321"
  }
]
```

### Get a Specific Todo
**GET** `/todos/{id}`

Response (200 OK):
```json
{
  "id": 1,
  "title": "Buy groceries",
  "completed": false,
  "created_at": "2024-01-15T10:30:00.123456"
}
```

Response (404 Not Found):
```json
{
  "detail": "Todo not found"
}
```

### Update a Todo
**PUT** `/todos/{id}`

Request body (all fields optional):
```json
{
  "title": "Buy groceries and cook dinner",
  "completed": true
}
```

Response (200 OK):
```json
{
  "id": 1,
  "title": "Buy groceries and cook dinner",
  "completed": true,
  "created_at": "2024-01-15T10:30:00.123456"
}
```

Response (404 Not Found):
```json
{
  "detail": "Todo not found"
}
```

### Delete a Todo
**DELETE** `/todos/{id}`

Response (204 No Content): Empty body

Response (404 Not Found):
```json
{
  "detail": "Todo not found"
}
```

## Project Structure

```
todo_rest_api/
├── main.py              # FastAPI application with all endpoints
├── requirements.txt     # Python dependencies
├── test_main.py        # Pytest test suite
└── README.md           # This file
```

## Data Model

Each todo has the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique identifier (auto-generated) |
| `title` | string | Todo item description |
| `completed` | boolean | Completion status (default: false) |
| `created_at` | datetime | ISO 8601 timestamp when the todo was created |

## Testing

The test suite (`test_main.py`) includes:

- **Creation tests** — verify todos are created with correct fields
- **Read tests** — verify retrieval of single and multiple todos
- **Update tests** — verify partial and full updates
- **Delete tests** — verify deletion and list updates
- **Not found tests** — verify 404 responses for invalid IDs
- **Integration tests** — verify complete CRUD workflows

All tests use FastAPI's `TestClient` and automatically clear in-memory storage between tests to ensure isolation.

## Example Usage

```python
import requests

BASE_URL = "http://localhost:8000"

# Create a todo
response = requests.post(f"{BASE_URL}/todos", json={"title": "Learn FastAPI"})
todo = response.json()
print(f"Created todo with ID: {todo['id']}")

# Get all todos
todos = requests.get(f"{BASE_URL}/todos").json()
print(f"Total todos: {len(todos)}")

# Update a todo
requests.put(f"{BASE_URL}/todos/{todo['id']}", json={"completed": True})

# Delete a todo
requests.delete(f"{BASE_URL}/todos/{todo['id']}")
```

## Development Notes

- Storage is in-memory and does not persist between server restarts
- IDs are auto-incremented integers starting from 1
- All timestamps are in ISO 8601 format with UTC timezone
- Partial updates are supported (send only the fields you want to change)

## License

MIT
