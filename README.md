# Task CRUD API

A SQLite-backed To-Do CRUD API built with Python and FastAPI for the FlyRank Backend Track Week 2 Assignment A1.

## Features

- Create, list, retrieve, update, and delete tasks
- Persistent SQLite storage in `tasks.db`
- Request validation with clear HTTP status codes
- Interactive Swagger documentation
- Automated CRUD test coverage

## Requirements

- Python 3.10 or later
- pip

The project uses Pydantic 2, which is installed automatically from `requirements.txt`.

## Setup

From this project directory, create and activate a virtual environment, then install dependencies.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python init_db.py
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python init_db.py
```

`init_db.py` is safe to run more than once. It creates the `tasks` table and seeds three example tasks only when the table is empty.

## Run the API

```bash
uvicorn app:app --reload
```

Open the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs). A health check is available at [http://localhost:8000/health](http://localhost:8000/health).

## API endpoints

| Method | Endpoint | Purpose | Success response |
| --- | --- | --- | --- |
| GET | `/` | API information | 200 |
| GET | `/health` | Health check | 200 |
| GET | `/tasks` | List every task | 200 |
| GET | `/tasks/{task_id}` | Get one task | 200 |
| POST | `/tasks` | Create a task | 201 |
| PUT | `/tasks/{task_id}` | Update one or both task fields | 200 |
| DELETE | `/tasks/{task_id}` | Delete a task | 204 |

### Task format

```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "done": false
}
```

### Request examples

Create a task:

```bash
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
```

Update its completion state:

```bash
curl -i -X PUT http://localhost:8000/tasks/1 -H "Content-Type: application/json" -d '{"done":true}'
```

Delete a task:

```bash
curl -i -X DELETE http://localhost:8000/tasks/1
```

Unknown task IDs return `404`. An empty update body returns `400`; malformed request data and invalid field values return FastAPI's standard `422` validation response.

## Test

Run the complete automated test suite with:

```bash
python -m unittest discover -s tests -v
```

Tests use an isolated temporary SQLite database and never alter `tasks.db`.

## SQLite inspection and SQL examples

Open `tasks.db` in **DB Browser for SQLite**, select the **Browse Data** tab, and choose the `tasks` table to view the stored records. Use the **Execute SQL** tab to run the following examples:

```sql
-- Read every task
SELECT id, title, done FROM tasks ORDER BY id;

-- Create a task
INSERT INTO tasks (title, done) VALUES ('Review SQLite queries', 0);

-- Mark that task complete
UPDATE tasks SET done = 1 WHERE title = 'Review SQLite queries';

-- Confirm the update
SELECT id, title, done FROM tasks WHERE title = 'Review SQLite queries';

-- Clean up the example row
DELETE FROM tasks WHERE title = 'Review SQLite queries';
```

After an `INSERT`, `UPDATE`, or `DELETE`, click **Write Changes** in DB Browser for SQLite to save it. For the required database screenshot, capture the Browse Data view with the `tasks` table selected and its task rows visible.

## Suggested Git history for submission

The assignment asks for a public GitHub repository with at least six meaningful commits. A sensible commit sequence is:

1. Initialize FastAPI server
2. Add root and health endpoints
3. Add read endpoints and missing-task handling
4. Add task creation and validation
5. Add update and delete endpoints
6. Add SQLite persistence, tests, and documentation
