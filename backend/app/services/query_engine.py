import duckdb
import pandas as pd


def create_connection():
    return duckdb.connect()


def register_dataframe(
    connection,
    dataframe: pd.DataFrame,
    table_name: str
):
    connection.register(table_name, dataframe)


def unregister_table(connection, table_name: str):
    """Remove a previously registered table/view from DuckDB."""
    try:
        connection.unregister(table_name)
    except Exception:
        # If the table was never registered or already removed,
        # swallow the error — this is a cleanup operation.
        pass


def execute_query(
    connection,
    query: str
):
    result = connection.execute(query).fetchdf()

    return {
        "columns": result.columns.tolist(),
        "rows": result.to_dict(orient="records"),
        "row_count": len(result)
    }