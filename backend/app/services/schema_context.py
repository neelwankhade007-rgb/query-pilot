def build_schema_context(dataset: dict) -> str:
    lines = []

    lines.append(f"Dataset: {dataset['filename']}")
    lines.append("Table: dataset")
    lines.append(f"Rows: {dataset['rows']}")
    lines.append("")
    lines.append("Columns:")

    for column_name, details in dataset["schema"].items():
        column_type = details["type"]
        nullable = details["nullable"]

        null_text = "nullable" if nullable else "not nullable"

        lines.append(
            f"- {column_name} → {column_type}, {null_text}"
        )

    return "\n".join(lines)