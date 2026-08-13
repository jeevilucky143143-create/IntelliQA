document.addEventListener('DOMContentLoaded', () => {
    loadDocuments();

    const fileInput = document.getElementById('file-input');
    const fileChosenSpan = document.getElementById('file-chosen-name');
    const uploadForm = document.getElementById('upload-form');

    if (fileInput) {
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                fileChosenSpan.innerText = fileInput.files[0].name;
            } else {
                fileChosenSpan.innerText = 'No file chosen';
            }
        });
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', (e) => {
            e.preventDefault();
            if (!fileInput.files.length) return;

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            fetch('/api/upload', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    showNotification('upload-alert', data.message, 'success');
                    fileInput.value = '';
                    fileChosenSpan.innerText = 'No file chosen';
                    loadDocuments();
                } else {
                    showNotification('upload-alert', data.error || 'Upload failed', 'error');
                }
            })
            .catch(err => {
                showNotification('upload-alert', 'Error uploading file', 'error');
            });
        });
    }
});

function loadDocuments() {
    const tbody = document.getElementById('documents-tbody');
    if (!tbody) return;

    fetch('/api/documents')
        .then(res => res.json())
        .then(data => {
            if (!data.documents || data.documents.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4">No documents found. Upload a file above.</td></tr>';
                return;
            }

            let rowsHtml = '';
            data.documents.forEach(doc => {
                rowsHtml += `
                    <tr>
                        <td><strong><i class="fa-solid fa-file-lines text-primary"></i> ${escapeHtml(doc.filename)}</strong></td>
                        <td><span class="badge badge-type">${doc.type}</span></td>
                        <td>${doc.passages_count} passages</td>
                        <td>${doc.size_kb} KB</td>
                        <td><span class="status-badge"><span class="status-dot"></span> Indexed</span></td>
                        <td>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteDocument('${escapeHtml(doc.filename)}')">
                                <i class="fa-solid fa-trash"></i> Delete
                            </button>
                        </td>
                    </tr>
                `;
            });
            tbody.innerHTML = rowsHtml;
        })
        .catch(err => {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-danger">Error loading documents.</td></tr>';
        });
}

function deleteDocument(filename) {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) return;

    fetch('/api/documents/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: filename })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            loadDocuments();
        } else {
            alert(data.error || 'Could not delete document.');
        }
    });
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
