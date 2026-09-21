import sqlite3
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import app


class TaskApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary_directory = tempfile.TemporaryDirectory()
        cls.database_path = Path(cls.temporary_directory.name) / "test_tasks.db"
        app.DATABASE_PATH = cls.database_path
        with sqlite3.connect(cls.database_path) as connection:
            connection.execute(
                "CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL, done BOOLEAN NOT NULL DEFAULT 0)"
            )
        cls.client = TestClient(app.app)

    @classmethod
    def tearDownClass(cls):
        cls.temporary_directory.cleanup()

    def setUp(self):
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("DELETE FROM tasks")

    def test_complete_crud_cycle(self):
        created = self.client.post("/tasks", json={"title": "Write tests"})
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json(), {"id": 1, "title": "Write tests", "done": False})

        listed = self.client.get("/tasks")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.json()), 1)

        updated = self.client.put("/tasks/1", json={"done": True})
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json(), {"id": 1, "title": "Write tests", "done": True})

        deleted = self.client.delete("/tasks/1")
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(self.client.get("/tasks/1").status_code, 404)

    def test_invalid_or_missing_tasks_return_expected_errors(self):
        self.assertEqual(self.client.post("/tasks", json={"title": ""}).status_code, 422)
        self.assertEqual(self.client.put("/tasks/1", json={"done": None}).status_code, 422)
        self.assertEqual(self.client.put("/tasks/1", json={}).status_code, 400)
        self.assertEqual(self.client.get("/tasks/99").status_code, 404)


if __name__ == "__main__":
    unittest.main()
