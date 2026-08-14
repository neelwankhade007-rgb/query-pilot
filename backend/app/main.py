import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.db.database import engine
from app.services.query_service import execute_query
from app.db.schema import get_database_schema
from app.services.llm_service import generate_sql
from app.services.sql_validator import validate_sql, SQLValidationError
from app.models.query import QueryRequest, QueryResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(SQLValidationError)
def sql_validation_exception_handler(request: Request, exc: SQLValidationError):
    logger.error(f"SQL Validation Error: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={
            "error": str(exc)
        }
    )

@app.get("/")
def root():
    return {"message": "QueryPilot API is running"}

@app.get("/db-test")
def db_test():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {"database": result.scalar()}

@app.get("/query-test")
def query_test():
    question = "Which customers bought a Laptop?"
    
    schema = get_database_schema()

    generated_sql = generate_sql(question, schema)

    try:
        validated_sql = validate_sql(generated_sql)
    except SQLValidationError as e:
        return {
            "question": question,
            "sql": generated_sql,
            "error": str(e)
        }

    result = execute_query(validated_sql)

    return {
        "question": question,
        "sql": validated_sql,
        "result": result
    }

@app.get("/schema")
def schema_test():
    return get_database_schema()

@app.get("/generate-sql")
def generate_sql_test():
    question = "Which customers brought a Laptop?"

    schema = get_database_schema()

    sql = generate_sql(question, schema)

    data = execute_query(sql)

    return {
        "question": question,
        "sql": sql,
    }

@app.post("/query", response_model=QueryResponse)
def query_database(request: QueryRequest):
    question = request.question

    schema = get_database_schema()

    try:
        generated_sql = generate_sql(question, schema)
    except ConnectionError as e:
        logger.error(f"Ollama Connection Error: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"error": "Failed to connect to Ollama. Please ensure Ollama is running (`ollama run qwen2.5-coder:7b`)."}
        )
    except Exception as e:
        logger.error(f"LLM Generation Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"LLM Error: {str(e)}"}
        )

    validated_sql = validate_sql(generated_sql, schema, question)

    result = execute_query(validated_sql)

    return {
        "question": question,
        "sql": validated_sql,
        "result": result
    }
