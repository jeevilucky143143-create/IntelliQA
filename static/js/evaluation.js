let modeChartInstance = null;
let accuracyChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    const btnRunEval = document.getElementById('btn-run-eval');
    if (btnRunEval) {
        btnRunEval.addEventListener('click', runEvaluation);
    }
});

function runEvaluation() {
    const btn = document.getElementById('btn-run-eval');
    const tbody = document.getElementById('eval-tbody');

    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Running Evaluation Suite...';
    tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4"><i class="fa-solid fa-spinner fa-spin text-primary"></i> Executing QA engines on 25+ benchmark questions...</td></tr>';

    fetch('/api/evaluate', { method: 'POST' })
        .then(res => res.json())
        .then(report => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-play"></i> Run Benchmark Evaluation';

            if (report.error) {
                alert(report.error);
                return;
            }

            const s = report.summary;
            document.getElementById('eval-total').innerText = s.total_questions;
            document.getElementById('eval-em').innerText = Math.round(s.exact_match_ratio * 100) + '%';
            document.getElementById('eval-f1').innerText = Math.round(s.f1_score * 100) + '%';
            document.getElementById('eval-precision').innerText = `${Math.round(s.precision * 100)}% / ${Math.round(s.recall * 100)}%`;
            document.getElementById('eval-conf').innerText = Math.round(s.average_confidence * 100) + '%';

            renderCharts(s);
            renderTable(report.details);
        })
        .catch(err => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-play"></i> Run Benchmark Evaluation';
            alert('Error executing evaluation pipeline.');
        });
}

function renderCharts(summary) {
    const modeCtx = document.getElementById('modeChart').getContext('2d');
    const accCtx = document.getElementById('accuracyChart').getContext('2d');

    const dist = summary.mode_distribution || { IR: 10, KNOWLEDGE: 10, DIALOGUE: 5 };

    if (modeChartInstance) modeChartInstance.destroy();
    if (accuracyChartInstance) accuracyChartInstance.destroy();

    // Mode Distribution Pie Chart
    modeChartInstance = new Chart(modeCtx, {
        type: 'doughnut',
        data: {
            labels: ['IR QA Mode', 'Knowledge Base QA', 'Dialogue Assistant'],
            datasets: [{
                data: [dist.IR || 0, dist.KNOWLEDGE || 0, dist.DIALOGUE || 0],
                backgroundColor: ['#A8DADC', '#CDB4DB', '#FFC8DD'],
                borderWidth: 2,
                borderColor: '#FFFFFF'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { font: { family: 'Inter' } } }
            }
        }
    });

    // Accuracy Bar Chart
    accuracyChartInstance = new Chart(accCtx, {
        type: 'bar',
        data: {
            labels: ['IR Accuracy', 'Knowledge Accuracy', 'Dialogue Accuracy', 'Overall F1'],
            datasets: [{
                label: 'Accuracy Score (%)',
                data: [
                    Math.round(summary.ir_accuracy * 100),
                    Math.round(summary.knowledge_accuracy * 100),
                    Math.round(summary.dialogue_accuracy * 100),
                    Math.round(summary.f1_score * 100)
                ],
                backgroundColor: ['#A8DADC', '#CDB4DB', '#FFC8DD', '#BDE0C0'],
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, max: 100, ticks: { callback: v => v + '%' } }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function renderTable(details) {
    const tbody = document.getElementById('eval-tbody');
    if (!details || details.length === 0) return;

    let html = '';
    details.forEach((item, idx) => {
        const emBadge = item.exact_match
            ? '<span class="status-badge text-success"><i class="fa-solid fa-check"></i> EM Match</span>'
            : '<span class="status-badge text-muted"><i class="fa-solid fa-xmark"></i> Partial</span>';

        const confPct = Math.round((item.confidence || 0) * 100);
        const f1Pct = Math.round((item.f1 || 0) * 100);

        html += `
            <tr>
                <td>${idx + 1}</td>
                <td><strong>${escapeHtml(item.question)}</strong></td>
                <td><small class="text-muted">${escapeHtml(item.expected)}</small></td>
                <td><span class="text-primary">${escapeHtml(item.predicted)}</span></td>
                <td><span class="mode-tag tag-${(item.mode || 'ir').toLowerCase()}">${escapeHtml(item.mode)}</span></td>
                <td>${emBadge}</td>
                <td><strong>${f1Pct}%</strong></td>
                <td>${confPct}%</td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
