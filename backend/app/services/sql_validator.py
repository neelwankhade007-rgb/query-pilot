import sqlglot
from sqlglot import exp 

class SQLValidationError(Exception):
    pass

def validate_sql(sql: str, schema: dict) -> str:
    """
    Validate that the generated SQL is:
    1. Non-empty
    2. A single statement
    3. Read-only
    4. Uses only tables that exist in the database schema
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
    
    # Tables that actually exist in our database
    allowed_tables = set(schema.keys())

    # Tables referenced by the generated SQL
    referenced_tables = {
        table.name
        for table in statement.find_all(exp.Table)
    }

    unknown_tables = referenced_tables - allowed_tables

    if unknown_tables:
        raise SQLValidationError(
            f"Unknown tables: {', '.join(unknown_tables)}"
        )

    return statement.sql(dialect="postgres")