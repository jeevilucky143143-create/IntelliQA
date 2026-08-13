document.addEventListener('DOMContentLoaded', () => {
    loadKnowledgeRecords();

    const addKbForm = document.getElementById('add-kb-form');
    if (addKbForm) {
        addKbForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const entity = document.getElementById('kb-entity').value.trim();
            const attribute = document.getElementById('kb-attribute').value.trim();
            const value = document.getElementById('kb-value').value.trim();
            const category = document.getElementById('kb-category').value.trim();
            const description = document.getElementById('kb-description').value.trim();

            if (!entity || !attribute || !value) return;

            fetch('/api/knowledge/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    entity: entity,
                    attribute: attribute,
                    value: value,
                    category: category,
                    description: description
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    closeAddModal();
                    loadKnowledgeRecords();
                } else {
                    alert(data.error || 'Failed to add record.');
                }
            });
        });
    }
});

function loadKnowledgeRecords() {
    const tbody = document.getElementById('kb-tbody');
    if (!tbody) return;

    fetch('/api/knowledge')
        .then(res => res.json())
        .then(data => {
            if (!data.records || data.records.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4">No knowledge records found.</td></tr>';
                return;
            }

            let rowsHtml = '';
            data.records.forEach(r => {
                rowsHtml += `
                    <tr>
                        <td>#${r.id}</td>
                        <td><strong>${escapeHtml(r.entity)}</strong></td>
                        <td><code>${escapeHtml(r.attribute)}</code></td>
                        <td><span class="text-purple font-weight-bold">${escapeHtml(r.value)}</span></td>
                        <td>${escapeHtml(r.category || 'General')}</td>
                        <td><small>${escapeHtml(r.source)}</small></td>
                        <td>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteKnowledgeRecord(${r.id})">
                                <i class="fa-solid fa-trash"></i> Delete
                            </button>
                        </td>
                    </tr>
                `;
            });
            tbody.innerHTML = rowsHtml;
        })
        .catch(err => {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-danger">Error loading records.</td></tr>';
        });
}

function filterKnowledgeTable() {
    const query = document.getElementById('kb-search-input').value.toLowerCase();
    const rows = document.querySelectorAll('#kb-tbody tr');

    rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(query) ? '' : 'none';
    });
}

function openAddModal() {
    document.getElementById('add-kb-modal').style.display = 'flex';
}

function closeAddModal() {
    document.getElementById('add-kb-modal').style.display = 'none';
    document.getElementById('add-kb-form').reset();
}

function deleteKnowledgeRecord(id) {
    if (!confirm('Are you sure you want to delete this record?')) return;

    fetch('/api/knowledge/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: id })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            loadKnowledgeRecords();
        } else {
            alert(data.error || 'Could not delete record.');
        }
    });
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
