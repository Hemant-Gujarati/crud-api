from contextlib import contextmanager
from pathlib import Path as FilePath
import sqlite3

from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, ConfigDict, Field, field_validator


DATABASE_PATH = FilePath(__file__).with_name("tasks.db")


class TaskCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    done: bool = False


class TaskUpdate(BaseModel):
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
    description="A small SQLite-backed CRUD API for managing to-do tasks.",
)


@contextmanager
def get_db():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def task_from_row(row: sqlite3.Row) -> TaskResponse:
    return TaskResponse(id=row["id"], title=row["title"], done=bool(row["done"]))


def get_existing_task(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row:
    row = connection.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
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
        cursor = connection.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)", (task.title, task.done)
        )
        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?", (cursor.lastrowid,)
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
        connection.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?", (title, done, task_id)
        )
        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
    return task_from_row(row)


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int = Path(ge=1)):
    with get_db() as connection:
        get_existing_task(connection, task_id)
        connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
