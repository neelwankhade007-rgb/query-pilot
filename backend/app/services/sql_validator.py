import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

class SQLValidationError(Exception):
    pass

def check_question_intent(question: str):
    if not question:
        return
    q_lower = question.lower().strip()
    
    mutation_verbs = ['delete', 'remove', 'drop', 'update', 'modify', 'insert', 'add', 'truncate', 'clear']
    read_prefix = ('show', 'list', 'get', 'find', 'select', 'count', 'how many', 'which', 'what', 'display', 'view')
    
    is_read = q_lower.startswith(read_prefix)
    
    for verb in mutation_verbs:
        if (q_lower.startswith(verb + ' ') or q_lower == verb or f' {verb} ' in f' {q_lower} ') and not is_read:
            if verb in ['delete', 'remove', 'clear', 'truncate', 'drop']:
                raise SQLValidationError("Cannot delete records: Only read-only SELECT queries are allowed.")
            elif verb in ['update', 'modify']:
                raise SQLValidationError("Cannot update records: Only read-only SELECT queries are allowed.")
            elif verb in ['insert', 'add']:
                raise SQLValidationError("Cannot insert records: Only read-only SELECT queries are allowed.")
            else:
                raise SQLValidationError("Cannot modify database: Only read-only SELECT queries are allowed.")

def validate_sql(sql: str, schema: dict, question: str = "") -> str:
    """
    Validate that the generated SQL is:
    1. Intent is read-only
    2. Non-empty
    3. A single statement
    4. Read-only
    5. Uses only tables that exist in the database schema
    """

    if question:
        check_question_intent(question)

    if not sql or not sql.strip():
        raise SQLValidationError("Generated SQL is empty.")
    
    try:
        statements = sqlglot.parse(sql, read="postgres")
    except ParseError as e:
        raise SQLValidationError(f"Invalid SQL syntax: {e}")
    
    # Allowing one SQL statement for now.
    if len(statements) != 1:
        raise SQLValidationError(f"Only one SQL statement is allowed.")
    
    statement = statements[0]

    # Only SELECT-style queries are allowed. 
    if not isinstance(statement, exp.Query):
        if isinstance(statement, exp.Delete):
            raise SQLValidationError("Cannot delete records: Only read-only SELECT queries are allowed.")
        elif isinstance(statement, exp.Update):
            raise SQLValidationError("Cannot update records: Only read-only SELECT queries are allowed.")
        elif isinstance(statement, exp.Insert):
            raise SQLValidationError("Cannot insert records: Only read-only SELECT queries are allowed.")
        elif isinstance(statement, (exp.Drop, exp.Create, exp.Alter)):
            raise SQLValidationError("Cannot modify database schema: DROP, CREATE, and ALTER are not allowed.")
        else:
            raise SQLValidationError("Cannot modify database: Only read-only SELECT queries are allowed.")
    
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