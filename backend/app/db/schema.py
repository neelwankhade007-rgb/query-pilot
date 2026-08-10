from sqlalchemy import inspect

from app.db.database import engine

def get_database_schema():
    inspector = inspect(engine)

    schema = {}

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)

        schema[table_name] = [
            {
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column["nullable"],
            }
            for column in columns
        ]

    return schema