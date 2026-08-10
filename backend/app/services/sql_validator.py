from sqlalchemy import exc
from os import read
import sqlglot
from sqlglot import exp 

class SQLValidationError(Exception):
    pass

def validate_sql(sql: str) -> str:
    """
    Validate that the generated SQL is a single, read-only PostgreSQL query.

    Returns:
        Cleaned SQL string.
    
    Raises: 
        SQLValidationError: If the SQL is invalid or not read-only.
    """

    if not sql or not sql.strip():
        raise SQLValidationError("Generated SQL is empty.")
    
    try:
        statements = sqlglot.parse(sql, read="postgres")
    except sqlglot.errors.ParseError as e:
        raise SQLValidationError(f"Invalid SQL: {e}")
    
    # Allowing one SQL statement for now.
    if len(statements) != 1:
        raise SQLValidationError(f"Only one SQL statement is allowed.")
    
    statement = statements[0]

    # Only SELECT-style queries are allowed. 
    if not isinstance(statement, exp.Query):
        raise SQLValidationError(
            "Only read-only SELECT queries are allowed."
        )

    return statement.sql(dialect="postgres")