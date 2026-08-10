from sqlalchemy import text

from app.db.database import engine

def execute_query(sql: str):
    with engine.connect() as connection:
        result = connection.execute(text(sql))
        
        columns = result.keys()
        rows = result.fetchall()

        return {
            "columns": list(columns),
            "rows": [list(row) for row in rows]
        }