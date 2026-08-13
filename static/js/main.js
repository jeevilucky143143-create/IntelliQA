/* Global Utilities for IntelliQA */

function showNotification(containerId, message, type = 'success') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.className = `alert-box alert-${type} mt-3`;
    container.innerHTML = message;
    container.style.display = 'block';
    
    setTimeout(() => {
        container.style.display = 'none';
    }, 4000);
}
