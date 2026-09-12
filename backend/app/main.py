import re
import uuid

from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.services.sql_validator import validate_sql
from app.services.sql_generator import generate_sql
from app.services.result_interpreter import interpret_result
from app.services.schema_context import build_schema_context
from app.models.query import QueryRequest
from app.services.dataset_manager import DatasetManager
from app.services.query_engine import (
    create_connection,
    execute_query
)


app = FastAPI(
    title="Query Pilot API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend():
        return FileResponse(FRONTEND_DIR / "index.html")




UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


db = create_connection()
dataset_manager = DatasetManager(db, upload_dir=str(UPLOAD_DIR))
dataset_manager.reload_datasets()


SUPPORTED_EXTENSIONS = {
    ".csv",
    ".json",
    ".xlsx",
    ".xls"
}

# Maximum upload file size: 100 MB
MAX_UPLOAD_BYTES = 100 * 1024 * 1024


def _sanitize_filename(filename: str) -> str:
    """Strip path components and replace unsafe characters."""

    # Take only the final path component (防止 directory traversal)
    name = Path(filename).name

    # Replace anything that isn't alphanumeric, dot, hyphen, or underscore
    name = re.sub(r"[^\w.\-]", "_", name)

    # Collapse consecutive underscores
    name = re.sub(r"_+", "_", name)

    # Ensure it isn't empty after sanitization
    if not name or name.startswith("."):
        name = "upload" + name

    return name


def _make_unique_path(directory: Path, filename: str) -> Path:
    """Generate a collision-free path by prefixing with a short UUID."""
    prefix = uuid.uuid4().hex[:8]
    safe_name = f"{prefix}_{filename}"
    return directory / safe_name


@app.get("/")
def root():
    return {
        "message": "Query Pilot backend is running"
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    original_filename = file.filename or "upload"
    extension = Path(original_filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only CSV, JSON and Excel files are supported."
        )

    # Sanitize and generate a unique filename
    safe_name = _sanitize_filename(original_filename)
    file_path = _make_unique_path(UPLOAD_DIR, safe_name)

    # Stream file to disk with size limit enforcement
    total_bytes = 0

    try:
        with open(file_path, "wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)  # 1 MB chunks

                if not chunk:
                    break

                total_bytes += len(chunk)

                if total_bytes > MAX_UPLOAD_BYTES:
                    # Clean up partial file
                    buffer.close()
                    file_path.unlink(missing_ok=True)

                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Maximum size is "
                               f"{MAX_UPLOAD_BYTES // (1024 * 1024)} MB."
                    )

                buffer.write(chunk)

    except HTTPException:
        raise

    except Exception as e:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )

    # Process and register dataset
    try:
        dataset = dataset_manager.add_dataset(
            file_path=str(file_path),
            original_filename=original_filename,
        )

        return {
            "success": True,
            "dataset": dataset
        }

    except Exception as e:
        # Clean up the saved file if processing fails
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail=f"Could not process file: {str(e)}"
        )


@app.get("/datasets")
def get_datasets():

    return {
        "success": True,
        "datasets": dataset_manager.get_all_datasets()
    }


@app.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: str):

    dataset = dataset_manager.get_dataset(dataset_id)

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found."
        )

    return {
        "success": True,
        "dataset": dataset
    }


@app.delete("/datasets/{dataset_id}")
def delete_dataset(dataset_id: str):

    deleted = dataset_manager.delete_dataset(dataset_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found."
        )

    return {
        "success": True,
        "message": "Dataset deleted."
    }


@app.post("/datasets/{dataset_id}/query")
async def query_dataset(
    dataset_id: str,
    request: QueryRequest
):

    dataset = dataset_manager.get_dataset(dataset_id)

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found."
        )

    try:
        result = execute_query(
            db,
            request.query
        )

        return {
            "success": True,
            "dataset_id": dataset_id,
            "query": request.query,
            "result": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Query failed: {str(e)}"
        )

@app.get("/datasets/{dataset_id}/context")
def get_dataset_context(dataset_id: str):

    dataset = dataset_manager.get_dataset(dataset_id)

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found."
        )

    context = build_schema_context(dataset)

    return {
        "success": True,
        "context": context
    }


@app.post("/datasets/{dataset_id}/generate-sql")
async def generate_dataset_sql(
    dataset_id: str,
    request: QueryRequest
):

    dataset = dataset_manager.get_dataset(dataset_id)

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found."
        )

    context = build_schema_context(dataset)

    try:
        sql = generate_sql(
            request.query,
            context
        )

        return {
            "success": True,
            "dataset_id": dataset_id,
            "question": request.query,
            "sql": sql
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"SQL generation failed: {str(e)}"
        )


@app.post("/datasets/{dataset_id}/ask")
async def ask_dataset(dataset_id: str, request: QueryRequest):

    # 1. Find dataset
    dataset = dataset_manager.get_dataset(dataset_id)

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found."
        )

    # 2. Build schema context
    context = build_schema_context(dataset)

    # 3. Generate SQL using Ollama
    try:
        sql = generate_sql(
            request.query,
            context
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"SQL generation failed: {str(e)}"
        )

    # 4. Validate generated SQL
    is_valid, message = validate_sql(sql)

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Generated SQL rejected: {message}"
        )
    
    actual_table = dataset["table_name"]

    sql_to_execute = re.sub(
        r"\bdataset\b",
        actual_table,
        sql,
        flags=re.IGNORECASE
    )

    # 5. Execute SQL
    try:
        result = execute_query(
            db,
            sql_to_execute
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Query execution failed: {str(e)}",
                "generated_sql": sql,
                "executed_sql": sql_to_execute,
            }
        )

    # 6. Interpret the result using Ollama
    answer = interpret_result(
        question=request.query,
        schema_context=context,
        sql=sql,
        result=result,
    )

    if answer is None:
        answer = "Could not generate an interpretation. See the raw result below."

    # 7. Return everything
    return {
        "success": True,
        "dataset_id": dataset_id,
        "question": request.query,
        "sql": sql,
        "answer": answer,
        "result": result
    }