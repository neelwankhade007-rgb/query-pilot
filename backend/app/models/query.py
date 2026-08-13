from pydantic import BaseModel, Field
from typing import Any

class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Natural language question about the database"
    )

class QueryResult(BaseModel):
    columns: list[str]
    rows: list[list[Any]]

class QueryResponse(BaseModel):
    question: str
    sql: str
    result: QueryResult