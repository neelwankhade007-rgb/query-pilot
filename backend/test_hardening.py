"""Comprehensive test for hardened upload, delete, and persistence."""
import httpx

BASE = "http://localhost:8000"


def section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def test(label, passed):
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {label}")
    return passed


all_passed = True


# ── 1. Clean slate ──────────────────────────────────────────

section("1. Clean slate — no datasets after fresh DB")
resp = httpx.get(f"{BASE}/datasets")
data = resp.json()
count = len(data["datasets"])
all_passed &= test(f"Dataset count is 0 (got {count})", count == 0)


# ── 2. Upload with safe filename ────────────────────────────

section("2. Upload — safe filename generation")
with open("testdata/employee_dataset.csv", "rb") as f:
    resp = httpx.post(
        f"{BASE}/upload",
        files={"file": ("../../etc/passwd.csv", f, "text/csv")},
    )
ds1 = resp.json()
all_passed &= test("Upload succeeded", ds1["success"])

# The original (malicious) filename should be stored for display,
# but the file on disk should NOT be at ../../etc/passwd.csv
file_path = ds1["dataset"]["file_path"]
all_passed &= test(
    f"File path is safe (no traversal): {file_path}",
    ".." not in file_path and "etc" not in file_path
)

dataset_id_1 = ds1["dataset"]["id"]
print(f"  Dataset 1 ID: {dataset_id_1}")


# ── 3. Duplicate filename — no collision ────────────────────

section("3. Duplicate filename — no collision")
with open("testdata/employee_dataset.csv", "rb") as f:
    resp = httpx.post(
        f"{BASE}/upload",
        files={"file": ("employee_dataset.csv", f, "text/csv")},
    )
ds2 = resp.json()
all_passed &= test("Second upload succeeded", ds2["success"])

dataset_id_2 = ds2["dataset"]["id"]
all_passed &= test(
    "Different dataset IDs",
    dataset_id_1 != dataset_id_2,
)
all_passed &= test(
    "Different file paths on disk",
    ds1["dataset"]["file_path"] != ds2["dataset"]["file_path"],
)
print(f"  Dataset 2 ID: {dataset_id_2}")


# ── 4. Unsupported extension ───────────────────────────────

section("4. Unsupported extension rejected")
resp = httpx.post(
    f"{BASE}/upload",
    files={"file": ("malware.exe", b"bad content", "application/octet-stream")},
)
all_passed &= test(f"Status 400 (got {resp.status_code})", resp.status_code == 400)


# ── 5. Dataset listing ─────────────────────────────────────

section("5. Dataset listing")
resp = httpx.get(f"{BASE}/datasets")
datasets = resp.json()["datasets"]
all_passed &= test(f"2 datasets listed (got {len(datasets)})", len(datasets) == 2)


# ── 6. Dataset details ─────────────────────────────────────

section("6. Dataset details")
resp = httpx.get(f"{BASE}/datasets/{dataset_id_1}")
all_passed &= test("GET dataset 1: 200", resp.status_code == 200)
ds_detail = resp.json()["dataset"]
all_passed &= test(f"Has schema with {len(ds_detail['schema'])} columns", len(ds_detail["schema"]) == 4)
all_passed &= test(f"Has {ds_detail['rows']} rows", ds_detail["rows"] == 25)


# ── 7. Query works on both datasets ────────────────────────

section("7. Query works on dataset 1")
resp = httpx.post(
    f"{BASE}/datasets/{dataset_id_1}/ask",
    json={"query": "How many employees are there?"},
    timeout=180,
)
if resp.status_code == 200:
    result = resp.json()
    all_passed &= test(f"Answer: {result['answer']}", True)
else:
    all_passed &= test(f"Ask failed: {resp.status_code}", False)


# ── 8. DELETE dataset ───────────────────────────────────────

section("8. DELETE dataset")
resp = httpx.delete(f"{BASE}/datasets/{dataset_id_1}")
all_passed &= test(f"DELETE status 200 (got {resp.status_code})", resp.status_code == 200)
all_passed &= test("Response says success", resp.json().get("success"))

# Verify it's gone
resp = httpx.get(f"{BASE}/datasets/{dataset_id_1}")
all_passed &= test(f"GET deleted dataset: 404 (got {resp.status_code})", resp.status_code == 404)

# Verify listing updated
resp = httpx.get(f"{BASE}/datasets")
datasets = resp.json()["datasets"]
all_passed &= test(f"1 dataset remaining (got {len(datasets)})", len(datasets) == 1)

# Double-delete should 404
resp = httpx.delete(f"{BASE}/datasets/{dataset_id_1}")
all_passed &= test(f"Double-delete: 404 (got {resp.status_code})", resp.status_code == 404)


# ── 9. Remaining dataset still works ───────────────────────

section("9. Remaining dataset still queryable")
resp = httpx.post(
    f"{BASE}/datasets/{dataset_id_2}/ask",
    json={"query": "What is the highest salary?"},
    timeout=180,
)
if resp.status_code == 200:
    result = resp.json()
    all_passed &= test(f"Answer: {result['answer']}", True)
else:
    all_passed &= test(f"Ask failed: {resp.status_code}", False)


# ── Summary ─────────────────────────────────────────────────

section("SUMMARY")
if all_passed:
    print("  All tests PASSED!")
else:
    print("  Some tests FAILED — check output above.")
