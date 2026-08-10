from fastapi import FastAPI
from sqlalchemy import text

from app.db.database import engine
from app.services.query_service import execute_query
from app.db.schema import get_database_schema
from app.services.llm_service import generate_sql
from app.services.sql_validator import validate_sql, SQLValidationError

app = FastAPI()

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
