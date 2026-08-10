// Query-Pilot Dashboard Vanilla JavaScript

document.addEventListener('DOMContentLoaded', () => {
    const queryInput = document.getElementById('query-input');
    const runQueryBtn = document.getElementById('run-query-btn');
    const emptyState = document.getElementById('empty-state');
    const resultsTable = document.getElementById('results-table');
    const resultsHead = document.getElementById('results-head');
    const resultsBody = document.getElementById('results-body');
    const resultsStats = document.getElementById('results-stats');
    const rowCountEl = document.getElementById('row-count');
    const executionTimeEl = document.getElementById('execution-time');

    // Key shortcut: Ctrl/Cmd + Enter to trigger query execution
    if (queryInput && runQueryBtn) {
        queryInput.addEventListener('keydown', (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
                e.preventDefault();
                runQueryBtn.click();
            }
        });
    }

    /**
     * Display query results dynamically
     * @param {Array<Object>} rows - Array of objects returned from backend SQL query
     * @param {number} executionTimeMs - Query execution duration in ms
     */
    window.renderQueryResults = function(rows = [], executionTimeMs = 0) {
        if (!rows || rows.length === 0) {
            emptyState.classList.remove('hidden');
            emptyState.textContent = 'No records returned for this query.';
            resultsTable.classList.add('hidden');
            resultsStats.classList.add('hidden');
            return;
        }

        // Extract column names from first row
        const columns = Object.keys(rows[0]);

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
    };

    function escapeHtml(str) {
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
