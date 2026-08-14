// Query-Pilot Dashboard Vanilla JavaScript

document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = 'http://127.0.0.1:8000';

    const queryInput = document.getElementById('query-input');
    const runQueryBtn = document.getElementById('run-query-btn');
    const emptyState = document.getElementById('empty-state');
    const resultsTable = document.getElementById('results-table');
    const resultsHead = document.getElementById('results-head');
    const resultsBody = document.getElementById('results-body');
    const resultsStats = document.getElementById('results-stats');
    const rowCountEl = document.getElementById('row-count');
    const executionTimeEl = document.getElementById('execution-time');

    const sqlSection = document.getElementById('sql-section');
    const sqlCode = document.getElementById('sql-code');
    const copySqlBtn = document.getElementById('copy-sql-btn');
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');

    // Key shortcut: Ctrl/Cmd + Enter to trigger query execution
    if (queryInput && runQueryBtn) {
        queryInput.addEventListener('keydown', (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
                e.preventDefault();
                runQueryBtn.click();
            }
        });

        runQueryBtn.addEventListener('click', () => handleRunQuery());
    }

    if (copySqlBtn && sqlCode) {
        copySqlBtn.addEventListener('click', () => {
            if (sqlCode.textContent) {
                navigator.clipboard.writeText(sqlCode.textContent);
                const originalText = copySqlBtn.innerHTML;
                copySqlBtn.innerHTML = `<span class="material-symbols-outlined text-[14px]">check</span> Copied!`;
                setTimeout(() => {
                    copySqlBtn.innerHTML = originalText;
                }, 2000);
            }
        });
    }

    async function handleRunQuery() {
        const question = queryInput.value.trim();
        if (!question) return;

        // Reset UI states
        hideError();
        setLoading(true);

        const startTime = performance.now();

        try {
            const response = await fetch(`${API_BASE_URL}/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question })
            });

            const endTime = performance.now();
            const executionTimeMs = Math.round(endTime - startTime);

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.error || errData.detail || `Server returned status ${response.status}`);
            }

            const data = await response.json();

            // Display Translated SQL
            if (data.sql) {
                sqlCode.textContent = data.sql;
                sqlSection.classList.remove('hidden');
            } else {
                sqlSection.classList.add('hidden');
            }

            // Transform backend columns & rows array into list of objects for table renderer
            const columns = data.result?.columns || [];
            const rawRows = data.result?.rows || [];

            const formattedRows = rawRows.map(row => {
                const obj = {};
                columns.forEach((col, idx) => {
                    obj[col] = row[idx];
                });
                return obj;
            });

            renderQueryResults(formattedRows, columns, executionTimeMs);

        } catch (err) {
            const msg = err.message.startsWith('Error') ? err.message : `Error: ${err.message}`;
            showError(msg);
            sqlSection.classList.add('hidden');
            emptyState.classList.remove('hidden');
            emptyState.textContent = 'Query execution failed.';
            resultsTable.classList.add('hidden');
            resultsStats.classList.add('hidden');
        } finally {
            setLoading(false);
        }
    }

    function setLoading(isLoading) {
        if (isLoading) {
            runQueryBtn.disabled = true;
            runQueryBtn.classList.add('opacity-75', 'cursor-not-allowed');
            runQueryBtn.innerHTML = `
                <span class="material-symbols-outlined text-[16px] animate-spin">progress_activity</span>
                Translating...
            `;
        } else {
            runQueryBtn.disabled = false;
            runQueryBtn.classList.remove('opacity-75', 'cursor-not-allowed');
            runQueryBtn.innerHTML = `
                <span class="material-symbols-outlined text-[16px]" data-icon="play_arrow">play_arrow</span>
                Run Query
            `;
        }
    }

    function showError(msg) {
        if (errorMessage && errorContainer) {
            errorMessage.textContent = msg;
            errorContainer.classList.remove('hidden');
        }
    }

    function hideError() {
        if (errorContainer) {
            errorContainer.classList.add('hidden');
        }
    }

    /**
     * Display query results dynamically
     * @param {Array<Object>} rows - Array of objects returned from backend SQL query
     * @param {Array<string>} columns - Column headers list
     * @param {number} executionTimeMs - Query execution duration in ms
     */
    function renderQueryResults(rows = [], columns = [], executionTimeMs = 0) {
        if (!columns || columns.length === 0 || !rows || rows.length === 0) {
            emptyState.classList.remove('hidden');
            emptyState.textContent = 'No records returned for this query.';
            resultsTable.classList.add('hidden');
            resultsStats.classList.add('hidden');
            return;
        }

        // Render Table Header
        resultsHead.innerHTML = `
            <tr>
                ${columns.map(col => `<th class="px-md py-sm font-semibold capitalize">${escapeHtml(col)}</th>`).join('')}
            </tr>
        `;

        // Render Table Rows
        resultsBody.innerHTML = rows.map((row, idx) => `
            <tr class="${idx < rows.length - 1 ? 'border-b border-surface-variant/50' : ''} hover:bg-surface-container-low transition-colors">
                ${columns.map(col => `<td class="px-md py-sm">${escapeHtml(String(row[col] ?? ''))}</td>`).join('')}
            </tr>
        `).join('');

        // Display stats
        rowCountEl.textContent = `${rows.length} ${rows.length === 1 ? 'row' : 'rows'} returned`;
        executionTimeEl.textContent = `Execution time: ${executionTimeMs}ms`;

        // Show table & stats, hide empty state
        emptyState.classList.add('hidden');
        resultsTable.classList.remove('hidden');
        resultsStats.classList.remove('hidden');
    }

    function escapeHtml(str) {
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});

