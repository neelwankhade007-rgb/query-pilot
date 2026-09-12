import re


FORBIDDEN_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "REPLACE",
    "MERGE",
    "GRANT",
    "REVOKE",
]


def validate_sql(sql: str) -> tuple[bool, str]:

    if not sql or not sql.strip():
        return False, "SQL query is empty."

    sql = sql.strip()

    # Remove trailing semicolon
    if sql.endswith(";"):
        sql = sql[:-1].strip()

    # Only allow SELECT queries
    if not re.match(r"^SELECT\b", sql, re.IGNORECASE):
        return False, "Only SELECT queries are allowed."

    # Prevent multiple SQL statements
    if ";" in sql:
        return False, "Multiple SQL statements are not allowed."

    # Block dangerous SQL keywords
    for keyword in FORBIDDEN_KEYWORDS:
        pattern = rf"\b{keyword}\b"

        if re.search(pattern, sql, re.IGNORECASE):
            return False, "Query must reference the dataset."

    return True, "SQL is valid."