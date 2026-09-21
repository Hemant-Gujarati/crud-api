# Task CRUD API

A Postgres-backed To-Do CRUD API built with Python, FastAPI, and Docker for the FlyRank Backend Track Week 3 Assignment A3.

## Features

- Create, list, retrieve, update, and delete tasks
- Persistent Postgres storage in Docker volume
- Request validation with clear HTTP status codes
- Interactive Swagger documentation
- Fully containerized via Docker Compose

## Setup and Run the API

1. Provide the environment variable configuration by copying the example:
   ```bash
   cp .env.example .env
   ```
2. Start the application and database together in a single command:
   ```bash
   docker compose up
   ```

The application will start, the database will initialize, and any missing tables will be created automatically. The database will also be seeded with three example tasks on the first run.

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

### Request examples

Create a task:

```bash
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
```

List tasks:

```bash
curl -i http://localhost:8000/tasks
```


