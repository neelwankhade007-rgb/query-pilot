import json

import httpx


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"

# Maximum number of rows to send to the LLM for interpretation.
# Aggregate results (1 row) and small result sets are sent in full.
# Larger results are truncated to keep the prompt compact.
MAX_ROWS_FOR_LLM = 50


SYSTEM_INSTRUCTION = """
You are a data analyst assistant.

Your job is to interpret SQL query results and provide a concise,
helpful natural-language answer to the user's original question.

Rules:
1. Answer ONLY based on the data provided.
2. Be concise — one to three sentences at most.
3. Include key numbers and values from the result.
4. If the result is a list of rows, summarise it (e.g. count, highlights).
5. Do NOT generate SQL. Do NOT explain the SQL query.
6. Do NOT use markdown formatting.
7. If the result is empty, say so clearly.
"""


def _serialize_result_for_llm(result: dict) -> str:
    """Serialize query result to a compact string for the LLM prompt.

    Large result sets are truncated to MAX_ROWS_FOR_LLM rows to keep
    the prompt a reasonable size.  The total row count is always
    included so the LLM knows the full extent of the data.
    """
    columns = result.get("columns", [])
    rows = result.get("rows", [])
    total_row_count = result.get("row_count", len(rows))

    if total_row_count == 0:
        return "The query returned no rows."

    truncated = False

    if len(rows) > MAX_ROWS_FOR_LLM:
        display_rows = rows[:MAX_ROWS_FOR_LLM]
        truncated = True
    else:
        display_rows = rows

    lines = []
    lines.append(f"Columns: {', '.join(columns)}")
    lines.append(f"Total rows: {total_row_count}")

    if truncated:
        lines.append(
            f"(Showing first {MAX_ROWS_FOR_LLM} of {total_row_count} rows)"
        )

    lines.append("")
    lines.append(json.dumps(display_rows, default=str))

    return "\n".join(lines)


def interpret_result(
    question: str,
    schema_context: str,
    sql: str,
    result: dict,
) -> str:
    """Use Ollama to interpret a query result and return a natural-language
    answer.  Returns a fallback message if interpretation fails."""

    serialized_result = _serialize_result_for_llm(result)

    prompt = f"""
{SYSTEM_INSTRUCTION}

Dataset context:
{schema_context}

User question:
{question}

SQL query that was executed:
{sql}

Query result:
{serialized_result}

Answer:
"""

    try:
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
            timeout=120,
        )
        response.raise_for_status()

        answer = response.json()["response"].strip()

        # Guard: reject empty answers
        if not answer:
            return None

        return answer

    except Exception:
        # Interpretation is best-effort. Return None so the caller
        # can fall back to returning the raw result without crashing.
        return None
