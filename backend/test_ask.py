"""Test the /ask endpoint with multiple natural-language questions."""
import json
import httpx

BASE = "http://localhost:8000"

# 1. Upload the dataset
print("=" * 60)
print("Uploading dataset...")
with open("uploads/employee_dataset.csv", "rb") as f:
    resp = httpx.post(f"{BASE}/upload", files={"file": ("employee_dataset.csv", f, "text/csv")})
upload = resp.json()
dataset_id = upload["dataset"]["id"]
print(f"Dataset ID: {dataset_id}\n")

# 2. Test questions
questions = [
    "What employees earn more than 60000?",
    "What is the average salary?",
    "How many employees are younger than 28?",
    "Show me the top 3 highest paid employees.",
    "What is the most common interesting field?",
]

for q in questions:
    print("=" * 60)
    print(f"Question: {q}")
    print("-" * 60)

    resp = httpx.post(
        f"{BASE}/datasets/{dataset_id}/ask",
        json={"query": q},
        timeout=180,
    )

    if resp.status_code == 200:
        data = resp.json()
        print(f"SQL:    {data['sql']}")
        print(f"Answer: {data['answer']}")
        print(f"Rows:   {data['result']['row_count']}")
    else:
        print(f"ERROR {resp.status_code}: {resp.text}")

    print()

print("=" * 60)
print("All tests complete.")
