document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');
    const btnClearChat = document.getElementById('btn-clear-chat');
    const demoChips = document.querySelectorAll('.demo-chip');

    // Scroll chat to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Submit question form
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const query = userInput.value.strip ? userInput.value.strip() : userInput.value.trim();
        if (!query) return;

        appendUserMessage(query);
        userInput.value = '';
        showTyping(true);

        fetch('/api/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        })
        .then(res => res.json())
        .then(data => {
            showTyping(false);
            appendBotMessage(data);
        })
        .catch(err => {
            showTyping(false);
            appendBotMessage({
                answer: "An error occurred while connecting to the server.",
                mode: "ERROR",
                confidence: 0.0,
                source: "system"
            });
        });
    });

    // Append User Message Bubble
    function appendUserMessage(text) {
        const row = document.createElement('div');
        row.className = 'message-row user-row';
        row.innerHTML = `
            <div class="user-avatar"><i class="fa-solid fa-user"></i></div>
            <div class="message-content">
                <div class="message-bubble user-bubble">
                    <p>${escapeHtml(text)}</p>
                </div>
            </div>
        `;
        chatMessages.appendChild(row);
        scrollToBottom();
    }

    // Append Bot Message Bubble
    function appendBotMessage(data) {
        const row = document.createElement('div');
        row.className = 'message-row bot-row';

        const mode = data.mode || 'IR';
        let modeTagClass = 'tag-ir';
        let modeLabel = '[ IR-BASED QA ]';
        if (mode === 'KNOWLEDGE') {
            modeTagClass = 'tag-kb';
            modeLabel = '[ KNOWLEDGE-BASED QA ]';
        } else if (mode === 'DIALOGUE') {
            modeTagClass = 'tag-dialogue';
            modeLabel = '[ DIALOGUE ]';
        }

        const confidencePct = Math.round((data.confidence || 0.85) * 100);
        const sourceName = data.source || 'system';

        let passageHtml = '';
        if (data.passage) {
            passageHtml = `
                <div class="passage-card">
                    <strong><i class="fa-solid fa-quote-left"></i> Relevant Passage:</strong> "${escapeHtml(data.passage)}"
                </div>
            `;
        }

        let explanationHtml = '';
        if (data.search_explanation) {
            const exp = data.search_explanation;
            explanationHtml = `
                <details class="explanation-details">
                    <summary class="explanation-summary"><i class="fa-solid fa-circle-nodes"></i> How IntelliQA found this answer ▼</summary>
                    <div class="explanation-body">
                        <div><strong>Search Query:</strong> ${escapeHtml(exp.query || '')}</div>
                        <div><strong>Extracted Answer:</strong> ${escapeHtml(exp.extracted_answer || '')}</div>
                        ${exp.similarity_scores ? `<div><strong>Top Passage Scores:</strong> ${exp.similarity_scores.join(', ')}</div>` : ''}
                    </div>
                </details>
            `;
        }

        row.innerHTML = `
            <div class="bot-avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="message-content">
                <div class="message-bubble bot-bubble">
                    <p>${escapeHtml(data.answer || '')}</p>
                    ${passageHtml}
                    ${explanationHtml}
                </div>
                <div class="message-meta">
                    <span class="mode-tag ${modeTagClass}">${modeLabel}</span>
                    <span class="source-tag"><i class="fa-solid fa-file-code"></i> ${escapeHtml(sourceName)}</span>
                    <span class="confidence-tag"><i class="fa-solid fa-chart-line"></i> ${confidencePct}% Confidence</span>
                    ${data.context_used ? '<span class="context-tag text-purple"><i class="fa-solid fa-brain"></i> Context Resolved</span>' : ''}
                </div>
            </div>
        `;

        chatMessages.appendChild(row);
        scrollToBottom();
    }

    function showTyping(show) {
        typingIndicator.style.display = show ? 'flex' : 'none';
        if (show) scrollToBottom();
    }

    // Demo Chips handler
    demoChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const question = chip.getAttribute('data-question');
            if (question) {
                userInput.value = question;
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    });

    // Clear Context handler
    if (btnClearChat) {
        btnClearChat.addEventListener('click', () => {
            fetch('/api/clear-session', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    chatMessages.innerHTML = `
                        <div class="message-row bot-row">
                            <div class="bot-avatar"><i class="fa-solid fa-robot"></i></div>
                            <div class="message-content">
                                <div class="message-bubble bot-bubble">
                                    <p>Conversation session context cleared. How can I assist you now?</p>
                                </div>
                            </div>
                        </div>
                    `;
                });
        });
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }
});
