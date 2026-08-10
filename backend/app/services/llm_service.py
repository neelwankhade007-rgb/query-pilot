from ollama import chat


MODEL = "qwen2.5-coder:7b"


def generate_sql(question: str, schema: dict) -> str:
    prompt = f"""
You are a PostgreSQL SQL generator.

Convert the user's natural language question into a SQL query.

Database schema:
{schema}

User Question:
{question}

Rules:
- Generate valid PostgreSQL SQL.
- Use only tables and columns that exist in the provided schema.
- Return ONLY the SQL query.
- Do not include markdown.
- Do not explain anything.
"""

    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        options={
            "temperature": 0.1,
        },
    )

    sql = response["message"]["content"].strip()

    # Remove markdown code fences if the model returns them
    if sql.startswith("```"):
        lines = sql.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]

        sql = "\n".join(lines).strip()

    return sql