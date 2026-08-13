document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('network-graph');
    if (!container) return;

    fetch('/api/graph')
        .then(res => res.json())
        .then(data => {
            if (!data.nodes || data.nodes.length === 0) {
                container.innerHTML = '<div class="p-5 text-center text-muted">No graph nodes available. Add records in Knowledge Base first.</div>';
                return;
            }

            const nodes = new vis.DataSet(data.nodes);
            const edges = new vis.DataSet(data.edges);

            const options = {
                nodes: {
                    borderWidth: 2,
                    font: { face: 'Inter', size: 14 }
                },
                edges: {
                    font: { face: 'Inter', size: 11, align: 'top' },
                    smooth: { type: 'continuous' }
                },
                physics: {
                    barnesHut: {
                        gravitationalConstant: -3000,
                        centralGravity: 0.3,
                        springLength: 120
                    }
                },
                interaction: {
                    hover: true,
                    zoomView: true
                }
            };

            new vis.Network(container, { nodes, edges }, options);
        })
        .catch(err => {
            console.error('Error rendering graph:', err);
            container.innerHTML = '<div class="p-5 text-center text-danger">Error loading network graph visualization.</div>';
        });
});
