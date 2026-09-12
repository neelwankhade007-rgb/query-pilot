import httpx


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"


SYSTEM_INSTRUCTION = """
You are an expert SQL generator.

Your job is to convert a user's natural-language question
into a DuckDB SQL query.

Rules:
1. Generate ONLY SQL.
2. Do not use markdown.
3. Do not explain the query.
4. Use only tables and columns provided in the dataset context.
5. Never invent columns.
6. Use valid DuckDB SQL.
7. The dataset table provided in the context is the only table
   you should query.
"""


def generate_sql(question: str, schema_context: str) -> str:

    prompt = f"""
{SYSTEM_INSTRUCTION}

Dataset context:
{schema_context}

User question:
{question}

SQL:
"""

    response = httpx.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0
            }
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    sql = data["response"].strip()

    # Remove markdown fences if the model ignores the instruction
    if sql.startswith("```"):
        sql = sql.replace("```sql", "")
        sql = sql.replace("```", "")
        sql = sql.strip()

    return sql