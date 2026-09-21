from pathlib import Path
import sqlite3


DATABASE_PATH = Path(__file__).with_name("tasks.db")


def initialize_database() -> None:
    """Create the task table and insert sample data only on first setup."""
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0 CHECK (done IN (0, 1))
            )
            """
        )
        count = connection.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if count == 0:
            connection.executemany(
                "INSERT INTO tasks (id, title, done) VALUES (?, ?, ?)",
                [
                    (1, "Learn FastAPI", 0),
                    (2, "Build CRUD API", 0),
                    (3, "Test with Swagger", 1),
                ],
            )


if __name__ == "__main__":
    initialize_database()
    print(f"Database ready: {DATABASE_PATH}")
