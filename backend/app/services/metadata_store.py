import json
import sqlite3
from pathlib import Path


class MetadataStore:
    """SQLite-backed metadata store for dataset persistence."""

    def __init__(self, db_path: str = "metadata.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(
            db_path,
            check_same_thread=False
        )
        self.connection.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                id            TEXT PRIMARY KEY,
                filename      TEXT NOT NULL,
                file_path     TEXT NOT NULL,
                file_type     TEXT NOT NULL,
                rows          INTEGER NOT NULL,
                columns       INTEGER NOT NULL,
                schema        TEXT NOT NULL,
                duckdb_table  TEXT NOT NULL,
                created_at    TEXT NOT NULL
            )
        """)
        self.connection.commit()

    def save_dataset(self, dataset: dict):
        self.connection.execute(
            """
            INSERT OR REPLACE INTO datasets
                (id, filename, file_path, file_type, rows, columns,
                 schema, duckdb_table, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dataset["id"],
                dataset["filename"],
                dataset["file_path"],
                dataset["file_type"],
                dataset["rows"],
                dataset["columns"],
                json.dumps(dataset["schema"]),
                dataset["table_name"],
                dataset["created_at"],
            ),
        )
        self.connection.commit()

    def get_dataset(self, dataset_id: str) -> dict | None:
        cursor = self.connection.execute(
            "SELECT * FROM datasets WHERE id = ?",
            (dataset_id,),
        )
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_dict(row)

    def get_all_datasets(self) -> list[dict]:
        cursor = self.connection.execute(
            "SELECT * FROM datasets ORDER BY created_at"
        )
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def delete_dataset(self, dataset_id: str):
        self.connection.execute(
            "DELETE FROM datasets WHERE id = ?",
            (dataset_id,),
        )
        self.connection.commit()

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> dict:
        """Convert a SQLite row into the dataset dict format used
        throughout the application."""
        return {
            "id": row["id"],
            "filename": row["filename"],
            "file_path": row["file_path"],
            "file_type": row["file_type"],
            "rows": row["rows"],
            "columns": row["columns"],
            "schema": json.loads(row["schema"]),
            "table_name": row["duckdb_table"],
            "created_at": row["created_at"],
        }
