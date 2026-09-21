import os
import time
import psycopg
from psycopg import OperationalError
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://postgres:dev@localhost:5432/tasks")

def initialize_database() -> None:
    """Create the task table and insert sample data only on first setup."""
    retries = 5
    while retries > 0:
        try:
            with psycopg.connect(DATABASE_URL, autocommit=True) as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tasks (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        done BOOLEAN NOT NULL DEFAULT false
                    )
                    """
                )

                count = connection.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
                if count == 0:
                    connection.executemany(
                        "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                        [
                            ("Learn FastAPI", False),
                            ("Build CRUD API", False),
                            ("Test with Swagger", True),
                        ],
                    )
                break
        except OperationalError:
            retries -= 1
            print("Database not ready, waiting...")
            time.sleep(2)

if __name__ == "__main__":
    initialize_database()
    print("Database initialized and ready.")
