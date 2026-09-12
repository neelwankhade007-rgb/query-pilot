import uuid
import logging
from pathlib import Path
from datetime import datetime, timezone

from app.services.file_processor import process_file, load_file
from app.services.query_engine import register_dataframe, unregister_table
from app.services.metadata_store import MetadataStore


logger = logging.getLogger(__name__)


class DatasetManager:

    def __init__(self, connection, upload_dir: str = "uploads"):
        self.connection = connection
        self.upload_dir = Path(upload_dir)
        self.store = MetadataStore()

    def add_dataset(self, file_path: str, original_filename: str = None):
        """Process a file and register it as a new dataset.

        Args:
            file_path: Path to the file on disk (already saved).
            original_filename: The user-supplied filename (for display).
                               Falls back to the basename of file_path.
        """
        dataframe, metadata = process_file(file_path)

        dataset_id = str(uuid.uuid4())

        # DuckDB table names cannot contain arbitary characters,
        # So we create a safe internal table name.uuid
        table_name = f"dataset_{dataset_id.replace('-', '_')}"

        register_dataframe(
            self.connection,
            dataframe,
            table_name
        )

        # Use the original user-supplied filename for display,
        # but keep file_path pointing to the safe name on disk.
        display_name = original_filename or Path(file_path).name

        dataset = {
            "id": dataset_id,
            "table_name": table_name,
            "file_path": file_path,
            "filename": display_name,
            "file_type": metadata["file_type"],
            "rows": metadata["rows"],
            "columns": metadata["columns"],
            "schema": metadata["schema"],
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        # Persist to SQLite
        self.store.save_dataset(dataset)

        return dataset

    def get_dataset(self, dataset_id: str):
        return self.store.get_dataset(dataset_id)

    def get_all_datasets(self):
        return self.store.get_all_datasets()

    def delete_dataset(self, dataset_id: str) -> bool:
        """Delete a dataset: remove from DuckDB, SQLite, and disk.

        Returns True if the dataset existed and was deleted,
        False if it was not found.
        """
        dataset = self.store.get_dataset(dataset_id)

        if dataset is None:
            return False

        # 1. Unregister from DuckDB
        unregister_table(self.connection, dataset["table_name"])

        # 2. Delete the file from disk
        file_path = Path(dataset["file_path"])

        if file_path.exists():
            try:
                file_path.unlink()
            except OSError:
                logger.warning(
                    "Could not delete file %s for dataset %s",
                    file_path,
                    dataset_id,
                )

        # 3. Remove metadata from SQLite
        self.store.delete_dataset(dataset_id)

        logger.info("Deleted dataset %s (%s)", dataset_id, dataset["filename"])

        return True

    def reload_datasets(self):
        """Re-register all persisted datasets into DuckDB on startup.

        If a file has been deleted from disk since it was uploaded,
        the dataset is removed from SQLite and skipped.
        """
        datasets = self.store.get_all_datasets()

        loaded = 0
        removed = 0

        for dataset in datasets:
            file_path = Path(dataset["file_path"])

            if not file_path.exists():
                logger.warning(
                    "File missing, removing dataset %s (%s)",
                    dataset["id"],
                    dataset["file_path"],
                )
                self.store.delete_dataset(dataset["id"])
                removed += 1
                continue

            try:
                dataframe = load_file(str(file_path))

                register_dataframe(
                    self.connection,
                    dataframe,
                    dataset["table_name"],
                )

                loaded += 1

            except Exception:
                logger.exception(
                    "Failed to reload dataset %s (%s)",
                    dataset["id"],
                    dataset["file_path"],
                )
                self.store.delete_dataset(dataset["id"])
                removed += 1

        logger.info(
            "Dataset reload complete: %d loaded, %d removed",
            loaded,
            removed,
        )