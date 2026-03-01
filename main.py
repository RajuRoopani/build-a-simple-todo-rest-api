from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="Todo REST API", version="1.0.0")

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class TodoCreate(BaseModel):
    title: str


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None


class TodoResponse(BaseModel):
    id: int
    title: str
    completed: bool
    created_at: datetime


# ---------------------------------------------------------------------------
# In-memory storage
# ---------------------------------------------------------------------------

_todos: Dict[int, TodoResponse] = {}
_next_id: int = 1


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate) -> TodoResponse:
    """Create a new todo item."""
    global _next_id

    todo = TodoResponse(
        id=_next_id,
        title=payload.title,
        completed=False,
        created_at=datetime.now(),
    )
    _todos[_next_id] = todo
    _next_id += 1
    return todo


@app.get("/todos", response_model=List[TodoResponse], status_code=status.HTTP_200_OK)
def list_todos() -> List[TodoResponse]:
    """Return all todo items."""
    return list(_todos.values())


@app.get("/todos/{todo_id}", response_model=TodoResponse, status_code=status.HTTP_200_OK)
def get_todo(todo_id: int) -> TodoResponse:
    """Return a single todo item by ID."""
    todo = _todos.get(todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )
    return todo


@app.put("/todos/{todo_id}", response_model=TodoResponse, status_code=status.HTTP_200_OK)
def update_todo(todo_id: int, payload: TodoUpdate) -> TodoResponse:
    """Update an existing todo item (partial update supported)."""
    todo = _todos.get(todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    updated = todo.model_copy(
        update={
            k: v
            for k, v in payload.model_dump(exclude_unset=True).items()
            if v is not None or k == "completed"
        }
    )
    _todos[todo_id] = updated
    return updated


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int) -> None:
    """Delete a todo item by ID."""
    if todo_id not in _todos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )
    del _todos[todo_id]
