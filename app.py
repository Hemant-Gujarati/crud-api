import os
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, ConfigDict, Field, field_validator

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://postgres:dev@localhost:5432/tasks")


class TaskCreate(BaseModel):
    """The fields accepted when a task is created."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    done: bool = False


class TaskUpdate(BaseModel):
    """One or both editable task fields."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=200)
    done: bool | None = None

    @field_validator("title", "done")
    @classmethod
    def fields_cannot_be_null(cls, value):
        if value is None:
            raise ValueError("Task fields cannot be null")
        return value


class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool


app = FastAPI(
    title="Task API",
    version="1.0.0",
    description="A small Postgres-backed CRUD API for managing to-do tasks.",
)


@contextmanager
def get_db():
    """Open a Postgres connection and always close it after the request."""
    with psycopg.connect(DATABASE_URL, row_factory=dict_row, autocommit=True) as connection:
        yield connection


def task_from_row(row: dict) -> TaskResponse:
    return TaskResponse(id=row["id"], title=row["title"], done=bool(row["done"]))


def get_existing_task(connection: psycopg.Connection, task_id: int) -> dict:
    row = connection.execute(
        "SELECT id, title, done FROM tasks WHERE id = %s", (task_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return row


@app.get("/", summary="API information")
def root():
    return {"name": "Task API", "version": app.version, "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


@app.get("/tasks", response_model=list[TaskResponse], summary="List all tasks")
def list_tasks():
    with get_db() as connection:
        rows = connection.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()
    return [task_from_row(row) for row in rows]


@app.get("/tasks/{task_id}", response_model=TaskResponse, summary="Get one task")
def get_task(task_id: int = Path(ge=1)):
    with get_db() as connection:
        return task_from_row(get_existing_task(connection, task_id))


@app.post("/tasks", response_model=TaskResponse, status_code=201, summary="Create a task")
def create_task(task: TaskCreate):
    with get_db() as connection:
        row = connection.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done",
            (task.title, task.done)
        ).fetchone()
    return task_from_row(row)


@app.put("/tasks/{task_id}", response_model=TaskResponse, summary="Update a task")
def update_task(task: TaskUpdate, task_id: int = Path(ge=1)):
    updated_fields = task.model_dump(exclude_unset=True)
    if not updated_fields:
        raise HTTPException(status_code=400, detail="Provide title and/or done")

    with get_db() as connection:
        existing = get_existing_task(connection, task_id)
        title = updated_fields.get("title", existing["title"])
        done = updated_fields.get("done", bool(existing["done"]))
        row = connection.execute(
            "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done",
            (title, done, task_id)
        ).fetchone()
    return task_from_row(row)


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int = Path(ge=1)):
    with get_db() as connection:
        get_existing_task(connection, task_id)
        connection.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
