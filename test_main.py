"""Test suite for Todo REST API using FastAPI TestClient."""

import pytest
from fastapi.testclient import TestClient
from main import app, _todos


@pytest.fixture(autouse=True)
def clear_todos():
    """Clear in-memory storage before each test."""
    _todos.clear()
    yield
    _todos.clear()


client = TestClient(app)


# ---------------------------------------------------------------------------
# CREATE (POST /todos)
# ---------------------------------------------------------------------------


def test_create_todo():
    """Test creating a new todo item."""
    response = client.post("/todos", json={"title": "Test todo"})
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test todo"
    assert data["completed"] is False
    assert "created_at" in data


def test_create_todo_with_empty_title():
    """Test creating a todo with empty title should succeed (no validation in spec)."""
    response = client.post("/todos", json={"title": ""})
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == ""


def test_create_multiple_todos():
    """Test creating multiple todos generates unique IDs."""
    response1 = client.post("/todos", json={"title": "First todo"})
    response2 = client.post("/todos", json={"title": "Second todo"})
    
    assert response1.status_code == 201
    assert response2.status_code == 201
    data1 = response1.json()
    data2 = response2.json()
    assert data1["id"] != data2["id"]
    assert data1["title"] == "First todo"
    assert data2["title"] == "Second todo"


# ---------------------------------------------------------------------------
# READ (GET /todos and GET /todos/{id})
# ---------------------------------------------------------------------------


def test_get_todos_empty():
    """Test getting todos when list is empty."""
    response = client.get("/todos")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_todos():
    """Test retrieving all todos."""
    # Create a todo first
    create_response = client.post("/todos", json={"title": "Test todo"})
    assert create_response.status_code == 201
    
    # Get all todos
    response = client.get("/todos")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["title"] == "Test todo"
    assert data[0]["completed"] is False


def test_get_todos_multiple():
    """Test retrieving multiple todos."""
    # Create multiple todos
    client.post("/todos", json={"title": "Todo 1"})
    client.post("/todos", json={"title": "Todo 2"})
    client.post("/todos", json={"title": "Todo 3"})
    
    # Get all todos
    response = client.get("/todos")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(isinstance(todo, dict) for todo in data)
    assert all("id" in todo and "title" in todo for todo in data)


def test_get_todo_by_id():
    """Test retrieving a single todo by ID."""
    # Create a todo
    create_response = client.post("/todos", json={"title": "Test todo"})
    todo_id = create_response.json()["id"]
    
    # Get the todo
    response = client.get(f"/todos/{todo_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Test todo"
    assert data["completed"] is False
    assert "created_at" in data


def test_get_todo_not_found():
    """Test retrieving a non-existent todo."""
    response = client.get("/todos/9999")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Todo not found"


def test_get_todo_with_various_ids():
    """Test retrieving todos with different IDs."""
    ids = []
    for i in range(3):
        create_response = client.post("/todos", json={"title": f"Todo {i+1}"})
        ids.append(create_response.json()["id"])
    
    # Verify each can be retrieved
    for todo_id, expected_title in zip(ids, ["Todo 1", "Todo 2", "Todo 3"]):
        response = client.get(f"/todos/{todo_id}")
        assert response.status_code == 200
        assert response.json()["title"] == expected_title


# ---------------------------------------------------------------------------
# UPDATE (PUT /todos/{id})
# ---------------------------------------------------------------------------


def test_update_todo_completed():
    """Test updating a todo's completed status."""
    # Create a todo
    create_response = client.post("/todos", json={"title": "Test todo"})
    todo_id = create_response.json()["id"]
    
    # Update the todo
    response = client.put(f"/todos/{todo_id}", json={"completed": True})
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["completed"] is True
    assert data["title"] == "Test todo"


def test_update_todo_title():
    """Test updating a todo's title."""
    # Create a todo
    create_response = client.post("/todos", json={"title": "Original title"})
    todo_id = create_response.json()["id"]
    
    # Update the title
    response = client.put(f"/todos/{todo_id}", json={"title": "Updated title"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Updated title"
    assert data["completed"] is False


def test_update_todo_both_fields():
    """Test updating both title and completed status."""
    # Create a todo
    create_response = client.post("/todos", json={"title": "Original"})
    todo_id = create_response.json()["id"]
    
    # Update both fields
    response = client.put(f"/todos/{todo_id}", json={
        "title": "Updated",
        "completed": True
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Updated"
    assert data["completed"] is True


def test_update_todo_partial():
    """Test partial update (only one field)."""
    # Create a todo
    create_response = client.post("/todos", json={"title": "Test"})
    todo_id = create_response.json()["id"]
    
    # Update only completed, leaving title unchanged
    response = client.put(f"/todos/{todo_id}", json={"completed": True})
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test"  # Should remain unchanged
    assert data["completed"] is True


def test_update_todo_not_found():
    """Test updating a non-existent todo."""
    response = client.put("/todos/9999", json={"completed": True})
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Todo not found"


def test_update_todo_empty_body():
    """Test updating with empty body (no changes)."""
    # Create a todo
    create_response = client.post("/todos", json={"title": "Test"})
    todo_id = create_response.json()["id"]
    
    # Update with empty body
    response = client.put(f"/todos/{todo_id}", json={})
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test"
    assert data["completed"] is False


# ---------------------------------------------------------------------------
# DELETE (DELETE /todos/{id})
# ---------------------------------------------------------------------------


def test_delete_todo():
    """Test deleting a todo."""
    # Create a todo
    create_response = client.post("/todos", json={"title": "Test todo"})
    todo_id = create_response.json()["id"]
    
    # Delete the todo
    response = client.delete(f"/todos/{todo_id}")
    
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(f"/todos/{todo_id}")
    assert get_response.status_code == 404


def test_delete_todo_not_found():
    """Test deleting a non-existent todo."""
    response = client.delete("/todos/9999")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Todo not found"


def test_delete_and_verify_list():
    """Test that deleted todo is removed from the list."""
    # Create two todos
    create1 = client.post("/todos", json={"title": "Todo 1"})
    create2 = client.post("/todos", json={"title": "Todo 2"})
    
    id1 = create1.json()["id"]
    id2 = create2.json()["id"]
    
    # Delete the first one
    response = client.delete(f"/todos/{id1}")
    assert response.status_code == 204
    
    # Verify only the second todo remains
    list_response = client.get("/todos")
    data = list_response.json()
    assert len(data) == 1
    assert data[0]["id"] == id2


def test_delete_multiple_todos():
    """Test deleting multiple todos."""
    # Create three todos
    ids = []
    for i in range(3):
        create_response = client.post("/todos", json={"title": f"Todo {i+1}"})
        ids.append(create_response.json()["id"])
    
    # Delete all of them
    for todo_id in ids:
        response = client.delete(f"/todos/{todo_id}")
        assert response.status_code == 204
    
    # Verify list is empty
    list_response = client.get("/todos")
    assert list_response.json() == []


# ---------------------------------------------------------------------------
# Integration / Full CRUD workflows
# ---------------------------------------------------------------------------


def test_full_crud_workflow():
    """Test a complete CRUD workflow."""
    # CREATE
    create_response = client.post("/todos", json={"title": "Buy groceries"})
    assert create_response.status_code == 201
    todo = create_response.json()
    todo_id = todo["id"]
    assert todo["completed"] is False
    
    # READ
    get_response = client.get(f"/todos/{todo_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Buy groceries"
    
    # UPDATE
    update_response = client.put(f"/todos/{todo_id}", json={
        "title": "Buy groceries and cook",
        "completed": True
    })
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["title"] == "Buy groceries and cook"
    assert updated["completed"] is True
    
    # DELETE
    delete_response = client.delete(f"/todos/{todo_id}")
    assert delete_response.status_code == 204
    
    # Verify deleted
    verify_response = client.get(f"/todos/{todo_id}")
    assert verify_response.status_code == 404


def test_multiple_todos_crud():
    """Test CRUD operations on multiple todos."""
    # Create 3 todos
    todos = []
    for i in range(3):
        response = client.post("/todos", json={"title": f"Task {i+1}"})
        todos.append(response.json())
    
    # Verify all exist
    list_response = client.get("/todos")
    assert len(list_response.json()) == 3
    
    # Update the first one
    first_id = todos[0]["id"]
    client.put(f"/todos/{first_id}", json={"completed": True})
    
    # Delete the second one
    second_id = todos[1]["id"]
    client.delete(f"/todos/{second_id}")
    
    # Verify final state
    list_response = client.get("/todos")
    remaining = list_response.json()
    assert len(remaining) == 2
    assert any(t["id"] == first_id and t["completed"] is True for t in remaining)
    assert not any(t["id"] == second_id for t in remaining)
