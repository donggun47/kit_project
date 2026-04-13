document.addEventListener('DOMContentLoaded', () => {
    // 1. Core State
    const API_BASE = ""; 
    const chatInput = document.getElementById('chat-input');
    const chatHistory = document.getElementById('chat-history');
    const archiveList = document.getElementById('notes-ul');
    const modalIngest = document.getElementById('modal-ingest');
    const detailPane = document.getElementById('detail-pane');
    const sysStatus = document.getElementById('system-status');
    let currentSelectedId = null;

    // 2. Archive Loading Logic (With Cache-Busting)
    async function loadArchives() {
        if (!archiveList) return;
        archiveList.innerHTML = '<li class="loading">Syncing neural subjects...</li>';
        try {
            // Added cache: 'no-store' to force fresh data from Pinecone/DB
            const response = await fetch(`${API_BASE}/graph/data`, { cache: 'no-store' });
            const data = await response.json();
            
            archiveList.innerHTML = '';
            if (data.nodes && data.nodes.length > 0) {
                const topics = {};
                data.nodes.forEach(node => {
                    const topic = node.data.type || 'General';
                    if (!topics[topic]) topics[topic] = [];
                    topics[topic].push(node);
                });

                for (const [topic, nodes] of Object.entries(topics)) {
                    const section = document.createElement('div');
                    section.className = 'topic-group';
                    section.innerHTML = `<div class="topic-header">${topic}</div>`;
                    
                    nodes.reverse().forEach(node => {
                        const li = document.createElement('li');
                        li.className = 'note-item glass-morphism';
                        li.innerHTML = `<div class="title">${node.data.label}</div>`;
                        li.onclick = () => showNoteDetails(node.data, node.id);
                        section.appendChild(li);
                    });
                    archiveList.appendChild(section);
                }
            } else {
                archiveList.innerHTML = '<li class="empty-state">Neural archive is empty.</li>';
            }
        } catch (err) {
            console.error("Failed to load side archives:", err);
            archiveList.innerHTML = '<li class="error">Memory recovery failed.</li>';
        }
    }

    // 3. Detail Pane Logic
    function showNoteDetails(data, id) {
        currentSelectedId = id;
        document.getElementById('detail-title').textContent = data.label;
        document.getElementById('detail-type').textContent = data.type || 'study';
        document.getElementById('detail-id').textContent = id;
        document.getElementById('detail-content').textContent = data.content || 'No content available.';
        detailPane.classList.add('open');
    }

    function hideNoteDetails() {
        detailPane.classList.remove('open');
        currentSelectedId = null;
    }

    async function deleteNote() {
        if (!currentSelectedId) return;
        if (!confirm("Delete this memory from your archive?")) return;

        try {
            const response = await fetch(`${API_BASE}/archive/${currentSelectedId}`, { 
                method: 'DELETE',
                cache: 'no-store'
            });
            if (response.ok) {
                hideNoteDetails();
                loadArchives();
            }
        } catch (err) { alert("Delete failed."); }
    }

    // 4. Chat Logic (Bilingual Socratic Mirror)
    async function sendMessage() {
        const msg = chatInput.value.trim();
        if (!msg) return;

        appendMessage('user', msg);
        chatInput.value = '';
        if (sysStatus) sysStatus.textContent = "Socrates is thinking...";
        
        try {
            const response = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg }),
                cache: 'no-store'
            });

            if (response.ok) {
                const data = await response.json();
                appendMessage('ai', data.question);
                if (data.topic) document.getElementById('topic-badge').textContent = data.topic;
            } else {
                appendMessage('ai', "Neural link interrupted. Please try again.");
            }
        } catch (err) {
            appendMessage('ai', "Connection to neural core failed.");
        } finally {
            if (sysStatus) sysStatus.textContent = "Socrates Neural Core Active";
        }
    }

    function appendMessage(role, text) {
        const div = document.createElement('div');
        div.className = `msg ${role}`;
        div.textContent = text;
        chatHistory.appendChild(div);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // 5. Ingestion Logic (Enhanced with Global Guard to prevent duplicates)
    let isIngesting = false;
    async function submitIngestion() {
        const btn = document.getElementById('btn-submit-ingest');
        const titleInput = document.getElementById('ingest-title');
        const contentInput = document.getElementById('ingest-content');
        const title = titleInput.value.trim();
        const content = contentInput.value.trim();

        // Dual checking: Boolean guard + Button disabled status
        if (!title || !content || isIngesting || btn.disabled) return;
        
        isIngesting = true;
        const originalText = btn.textContent;
        btn.disabled = true;
        btn.textContent = "Syncing...";

        try {
            const response = await fetch(`${API_BASE}/ingest`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, content }),
                cache: 'no-store'
            });

            if (response.ok) {
                // Success: Immediate UI cleanup
                if (modalIngest) modalIngest.style.display = 'none';
                titleInput.value = '';
                contentInput.value = '';
                await loadArchives();
            } else {
                const errorData = await response.json();
                alert("Archive Sync Failed: " + (errorData.detail || "Unknown error"));
            }
        } catch (err) { 
            console.error(err);
            alert("Neural connection error during sync.");
        } finally { 
            isIngesting = false;
            if (btn) {
                btn.disabled = false; 
                btn.textContent = originalText;
            }
        }
    }

    // 6. Event Listeners
    const titleIn = document.getElementById('ingest-title');
    const contentIn = document.getElementById('ingest-content');

    // Title field: Enter to submit
    if (titleIn) {
        titleIn.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                submitIngestion();
            }
        });
    }

    // Content field: Ctrl + Enter to submit
    if (contentIn) {
        contentIn.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                submitIngestion();
            }
        });
    }

    const chatIn = document.getElementById('chat-input');
    if (chatIn) {
        chatIn.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    const setClick = (id, fn) => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('click', fn);
    };

    setClick('btn-ingest', () => {
        if (modalIngest) {
            modalIngest.style.display = 'flex';
            if (titleIn) titleIn.focus();
        }
    });
    setClick('btn-cancel', () => {
        if (modalIngest) modalIngest.style.display = 'none';
    });
    setClick('btn-submit-ingest', submitIngestion);
    
    const closeBtn = document.querySelector('.btn-close-pane');
    if (closeBtn) closeBtn.addEventListener('click', hideNoteDetails);
    
    setClick('btn-delete-archive', deleteNote);

    // 7. Initialize
    loadArchives();
    async function loadChatHistory() {
        try {
            const response = await fetch(`${API_BASE}/chat/history`, { cache: 'no-store' });
            const history = await response.json();
            if (history.length > 0) {
                chatHistory.innerHTML = '';
                history.forEach(m => appendMessage(m.role, m.content));
                const lastTopic = history[history.length - 1].topic;
                if (lastTopic) {
                    const badge = document.getElementById('topic-badge');
                    if (badge) badge.textContent = lastTopic;
                }
            }
        } catch (err) {}
    }
    loadChatHistory();
});
