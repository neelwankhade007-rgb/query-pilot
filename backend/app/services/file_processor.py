from pathlib import Path

import pandas as pd


SUPPORTED_EXTENSIONS = {".csv", ".json", ".xlsx", ".xls"}


def load_file(file_path: str) -> pd.DataFrame:
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".csv":
        return pd.read_csv(path)

    if extension == ".json":
        return pd.read_json(path)

    if extension in {".xlsx", ".xls"}:
        return pd.read_excel(path)

    raise ValueError(f"Unsupported file type: {extension}")


def get_column_type(series: pd.Series) -> str:
    if pd.api.types.is_integer_dtype(series):
        return "integer"

    if pd.api.types.is_float_dtype(series):
        return "float"

    if pd.api.types.is_bool_dtype(series):
        return "boolean"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    return "string"


def analyze_dataframe(df: pd.DataFrame) -> dict:
    columns = {}

    for column in df.columns:
        series = df[column]

        columns[str(column)] = {
            "type": get_column_type(series),
            "nullable": bool(series.isna().any()),
            "missing_values": int(series.isna().sum()),
            "unique_values": int(series.nunique(dropna=True))
        }

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "schema": columns
    }


def process_file(file_path: str):
    path = Path(file_path)

    df = load_file(file_path)
    analysis = analyze_dataframe(df)

    return df, {
        "filename": path.name,
        "file_type": path.suffix.lower(),
        **analysis
    }