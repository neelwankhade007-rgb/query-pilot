"""Quick smoke test for the persistence layer."""
import httpx
import time

BASE = "http://localhost:8000"

print("=" * 60)
print("TEST: Persistent dataset management")
print("=" * 60)

# 1. Check if the server reloaded datasets from the previous session
print("\n1. Checking existing datasets after restart...")
resp = httpx.get(f"{BASE}/datasets")
data = resp.json()
datasets = data["datasets"]
print(f"   Found {len(datasets)} dataset(s) from SQLite")

for ds in datasets:
    print(f"   - {ds['id'][:8]}... | {ds['filename']} | {ds['rows']} rows")

# 2. Upload a fresh dataset
print("\n2. Uploading employee_dataset.csv...")
with open("uploads/employee_dataset.csv", "rb") as f:
    resp = httpx.post(f"{BASE}/upload", files={"file": ("employee_dataset.csv", f, "text/csv")})
upload = resp.json()
dataset_id = upload["dataset"]["id"]
print(f"   New dataset ID: {dataset_id}")

# 3. Verify it appears in the list
print("\n3. Verifying dataset appears in GET /datasets...")
resp = httpx.get(f"{BASE}/datasets")
datasets = resp.json()["datasets"]
ids = [ds["id"] for ds in datasets]
assert dataset_id in ids, f"Dataset {dataset_id} not found in list!"
print(f"   OK — {len(datasets)} total dataset(s)")

# 4. Verify the dataset is queryable via /ask
print("\n4. Testing /ask on the new dataset...")
resp = httpx.post(
    f"{BASE}/datasets/{dataset_id}/ask",
    json={"query": "How many employees are there?"},
    timeout=180,
)
if resp.status_code == 200:
    result = resp.json()
    print(f"   SQL:    {result['sql']}")
    print(f"   Answer: {result['answer']}")
else:
    print(f"   ERROR {resp.status_code}: {resp.text}")

# 5. Check that previously loaded datasets (if any) are still queryable
if len(datasets) > 1:
    old = [ds for ds in datasets if ds["id"] != dataset_id][0]
    print(f"\n5. Testing /ask on previously persisted dataset {old['id'][:8]}...")
    resp = httpx.post(
        f"{BASE}/datasets/{old['id']}/ask",
        json={"query": "What is the average salary?"},
        timeout=180,
    )
    if resp.status_code == 200:
        result = resp.json()
        print(f"   SQL:    {result['sql']}")
        print(f"   Answer: {result['answer']}")
    else:
        print(f"   ERROR {resp.status_code}: {resp.text}")
else:
    print("\n5. Skipped (no previously persisted datasets to test)")

print("\n" + "=" * 60)
print("All persistence tests complete.")
print("=" * 60)
