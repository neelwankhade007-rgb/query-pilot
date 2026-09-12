/**
 * Query Pilot - Frontend Application Logic
 * Interacts with FastAPI backend at http://localhost:8000
 */

const API_BASE = window.location.origin.includes("localhost") || window.location.origin.includes("127.0.0.1")
  ? window.location.origin
  : "http://localhost:8000";

// State
let currentDatasets = [];
let activeDataset = null;
let selectedUploadFile = null;

// DOM Elements
const fileInput = document.getElementById("file-input");
const dropZone = document.getElementById("drop-zone");
const dropContent = document.getElementById("drop-content");
const selectedFileInfo = document.getElementById("selected-file-info");
const fileNameDisplay = document.getElementById("file-name-display");
const fileSizeDisplay = document.getElementById("file-size-display");
const removeFileBtn = document.getElementById("remove-file-btn");
const uploadBtn = document.getElementById("upload-btn");
const uploadSpinner = document.getElementById("upload-spinner");

const datasetList = document.getElementById("dataset-list");
const datasetCountDesc = document.getElementById("dataset-count-desc");
const refreshDatasetsBtn = document.getElementById("refresh-datasets-btn");

const emptyWorkspace = document.getElementById("empty-workspace");
const workspaceActive = document.getElementById("workspace-active");
const activeDatasetName = document.getElementById("active-dataset-name");
const activeDatasetRows = document.getElementById("active-dataset-rows");
const activeDatasetType = document.getElementById("active-dataset-type");
const activeDatasetTable = document.getElementById("active-dataset-table");

const toggleSchemaBtn = document.getElementById("toggle-schema-btn");
const schemaDrawer = document.getElementById("schema-drawer");
const schemaTags = document.getElementById("schema-tags");

const queryForm = document.getElementById("query-form");
const queryInput = document.getElementById("query-input");
const askBtn = document.getElementById("ask-btn");
const askLoading = document.getElementById("ask-loading");
const askText = askBtn.querySelector(".ask-text");

const queryProgressCard = document.getElementById("query-progress-card");
const progressStepTitle = document.getElementById("progress-step-title");
const progressStepDesc = document.getElementById("progress-step-desc");

const errorCard = document.getElementById("error-card");
const errorMessage = document.getElementById("error-message");

const resultsContainer = document.getElementById("results-container");
const answerContent = document.getElementById("answer-content");
const sqlCode = document.getElementById("sql-code");
const copyAnswerBtn = document.getElementById("copy-answer-btn");
const copySqlBtn = document.getElementById("copy-sql-btn");
const dataTable = document.getElementById("data-table");
const dataTableHead = document.getElementById("data-table-head");
const dataTableBody = document.getElementById("data-table-body");
const tableRowCount = document.getElementById("table-row-count");

const toastContainer = document.getElementById("toast-container");

// ==========================================
// Initialization
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  fetchDatasets();
  setupEventListeners();
});

function setupEventListeners() {
  // Drag & drop
  dropZone.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", handleFileSelect);

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("drag-over");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
    }
  });

  removeFileBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    clearSelectedFile();
  });

  uploadBtn.addEventListener("click", handleUpload);
  refreshDatasetsBtn.addEventListener("click", fetchDatasets);

  // Schema drawer toggle
  toggleSchemaBtn.addEventListener("click", () => {
    schemaDrawer.classList.toggle("hidden");
    toggleSchemaBtn.classList.toggle("open");
  });

  // Query form submission
  queryForm.addEventListener("submit", handleQuerySubmit);

  // Quick prompts
  document.querySelectorAll(".qp-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      queryInput.value = btn.getAttribute("data-query");
      queryInput.focus();
    });
  });

  // Copy buttons
  copyAnswerBtn.addEventListener("click", () => {
    navigator.clipboard.writeText(answerContent.innerText);
    showToast("Answer copied to clipboard!", "success");
  });

  copySqlBtn.addEventListener("click", () => {
    navigator.clipboard.writeText(sqlCode.innerText);
    showToast("SQL copied to clipboard!", "success");
  });
}

// ==========================================
// File Selection & Upload
// ==========================================
function handleFileSelect(e) {
  if (e.target.files && e.target.files.length > 0) {
    setFile(e.target.files[0]);
  }
}

function setFile(file) {
  selectedUploadFile = file;
  fileNameDisplay.textContent = file.name;
  fileSizeDisplay.textContent = formatBytes(file.size);

  dropContent.classList.add("hidden");
  selectedFileInfo.classList.remove("hidden");
  uploadBtn.disabled = false;
}

function clearSelectedFile() {
  selectedUploadFile = null;
  fileInput.value = "";
  dropContent.classList.remove("hidden");
  selectedFileInfo.classList.add("hidden");
  uploadBtn.disabled = true;
}

async function handleUpload() {
  if (!selectedUploadFile) return;

  const formData = new FormData();
  formData.append("file", selectedUploadFile);

  uploadBtn.disabled = true;
  uploadSpinner.classList.remove("hidden");

  try {
    const res = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail?.message || data.detail || "Upload failed");
    }

    showToast(`Dataset "${data.dataset.filename}" registered!`, "success");
    clearSelectedFile();
    await fetchDatasets();
    selectDataset(data.dataset.id);
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    uploadBtn.disabled = false;
    uploadSpinner.classList.add("hidden");
  }
}

// ==========================================
// Datasets Management
// ==========================================
async function fetchDatasets() {
  datasetCountDesc.textContent = "Updating...";
  try {
    const res = await fetch(`${API_BASE}/datasets`);
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Failed to load datasets");
    }

    currentDatasets = data.datasets || [];
    renderDatasetList();
  } catch (err) {
    datasetList.innerHTML = `<div class="list-placeholder" style="color: #f87171">Failed to connect to backend.<br><small>${err.message}</small></div>`;
    datasetCountDesc.textContent = "Offline";
  }
}

function renderDatasetList() {
  datasetCountDesc.textContent = `${currentDatasets.length} registered`;

  if (currentDatasets.length === 0) {
    datasetList.innerHTML = `<div class="list-placeholder">No datasets uploaded yet. Upload a CSV, JSON, or Excel file above.</div>`;
    return;
  }

  datasetList.innerHTML = "";
  currentDatasets.forEach((ds) => {
    const item = document.createElement("div");
    item.className = `dataset-item ${activeDataset && activeDataset.id === ds.id ? "active" : ""}`;
    item.dataset.id = ds.id;

    item.innerHTML = `
      <div class="ds-info">
        <span class="ds-filename" title="${escapeHtml(ds.filename)}">${escapeHtml(ds.filename)}</span>
        <div class="ds-meta-row">
          <span class="ds-badge">${(ds.file_type || "csv").toUpperCase()}</span>
          <span>${(ds.rows || 0).toLocaleString()} rows</span>
        </div>
      </div>
      <button class="ds-delete-btn" title="Delete dataset" data-id="${ds.id}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="3 6 5 6 21 6"/>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
        </svg>
      </button>
    `;

    item.addEventListener("click", (e) => {
      if (e.target.closest(".ds-delete-btn")) return;
      selectDataset(ds.id);
    });

    const deleteBtn = item.querySelector(".ds-delete-btn");
    deleteBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      deleteDataset(ds.id, ds.filename);
    });

    datasetList.appendChild(item);
  });
}

function selectDataset(datasetId) {
  const found = currentDatasets.find((d) => d.id === datasetId);
  if (!found) return;

  activeDataset = found;
  renderDatasetList(); // Update active highlight

  emptyWorkspace.classList.add("hidden");
  workspaceActive.classList.remove("hidden");

  // Populate active banner
  activeDatasetName.textContent = found.filename;
  activeDatasetRows.textContent = `${(found.rows || 0).toLocaleString()} rows`;
  activeDatasetType.textContent = (found.file_type || "csv").toUpperCase();
  activeDatasetTable.textContent = found.table_name || "dataset";

  // Populate Schema drawer
  schemaTags.innerHTML = "";
  const schema = found.schema || {};
  Object.entries(schema).forEach(([col, info]) => {
    const typeName = typeof info === "object" && info !== null ? (info.type || "unknown") : String(info);
    const tag = document.createElement("div");
    tag.className = "schema-column-tag";
    tag.innerHTML = `
      <span class="col-name">${escapeHtml(col)}</span>
      <span class="col-type">${escapeHtml(typeName)}</span>
    `;
    schemaTags.appendChild(tag);
  });


  // Reset results
  resultsContainer.classList.add("hidden");
  errorCard.classList.add("hidden");
  queryInput.focus();
}

async function deleteDataset(datasetId, filename) {
  if (!confirm(`Are you sure you want to delete "${filename}"?`)) return;

  try {
    const res = await fetch(`${API_BASE}/datasets/${datasetId}`, {
      method: "DELETE",
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Delete failed");
    }

    showToast(`Dataset deleted`, "info");
    if (activeDataset && activeDataset.id === datasetId) {
      activeDataset = null;
      workspaceActive.classList.add("hidden");
      emptyWorkspace.classList.remove("hidden");
    }
    await fetchDatasets();
  } catch (err) {
    showToast(err.message, "error");
  }
}

// ==========================================
// Natural Language Query Execution
// ==========================================
async function handleQuerySubmit(e) {
  e.preventDefault();
  if (!activeDataset) {
    showToast("Please select a dataset first", "error");
    return;
  }

  const queryText = queryInput.value.trim();
  if (!queryText) return;

  // UI state: loading
  askBtn.disabled = true;
  askText.classList.add("hidden");
  askLoading.classList.remove("hidden");

  errorCard.classList.add("hidden");
  resultsContainer.classList.add("hidden");
  queryProgressCard.classList.remove("hidden");

  // Multi-step progress animation timer
  progressStepTitle.textContent = "Translating question to SQL...";
  progressStepDesc.textContent = "Ollama is synthesizing your schema context into DuckDB SQL.";

  const progressTimeout = setTimeout(() => {
    progressStepTitle.textContent = "Executing Query & Interpreting...";
    progressStepDesc.textContent = "DuckDB finished execution. Ollama is generating an executive natural-language answer.";
  }, 12000);

  try {
    const res = await fetch(`${API_BASE}/datasets/${activeDataset.id}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: queryText }),
    });

    clearTimeout(progressTimeout);

    const data = await res.json();
    if (!res.ok) {
      const errDetail = data.detail;
      const msg = typeof errDetail === "object" ? errDetail.message || JSON.stringify(errDetail) : errDetail;
      throw new Error(msg || "Query processing failed");
    }

    renderResults(data);
  } catch (err) {
    clearTimeout(progressTimeout);
    showError(err.message);
  } finally {
    queryProgressCard.classList.add("hidden");
    askBtn.disabled = false;
    askText.classList.remove("hidden");
    askLoading.classList.add("hidden");
  }
}

function renderResults(data) {
  // 1. Natural Language Answer
  answerContent.innerText = data.answer || "No interpretation generated.";

  // 2. Generated SQL
  sqlCode.textContent = data.sql || "-- No SQL available";

  // 3. Tabular DuckDB Result
  const result = data.result || { columns: [], rows: [], row_count: 0 };
  const cols = result.columns || [];
  const rows = result.rows || [];

  tableRowCount.textContent = `${result.row_count ?? rows.length} row${rows.length === 1 ? "" : "s"}`;

  // Build the table header
  dataTableHead.innerHTML = `
    <tr>
      ${cols.map((col) => `<th>${escapeHtml(col)}</th>`).join("")}
    </tr>
  `;

  // Build the table body
  if (rows.length === 0) {
    dataTableBody.innerHTML = `<tr><td colspan="${Math.max(1, cols.length)}" style="text-align:center; padding: 24px; color: var(--text-dim);">No rows returned</td></tr>`;
  } else {
    dataTableBody.innerHTML = rows
      .map((row) => {
        const cells = Array.isArray(row)
          ? row
          : cols.map((col) => row[col]);
        return `
          <tr>
            ${cells.map((val) => `<td>${escapeHtml(val !== null && val !== undefined ? String(val) : "NULL")}</td>`).join("")}
          </tr>
        `;
      })
      .join("");
  }

  resultsContainer.classList.remove("hidden");
  resultsContainer.scrollIntoView({ behavior: "smooth", block: "start" });

}

function showError(msg) {
  errorMessage.textContent = msg;
  errorCard.classList.remove("hidden");
}

// ==========================================
// Utilities
// ==========================================
function formatBytes(bytes, decimals = 1) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
}

function escapeHtml(str) {
  if (typeof str !== "string") return str;
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;

  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(40px)";
    toast.style.transition = "all 0.3s ease-out";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
