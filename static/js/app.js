document.addEventListener('DOMContentLoaded', () => {
    // 1. Core State
    const API_BASE = ""; 
    const chatInput = document.getElementById('chat-input');
    const chatHistory = document.getElementById('chat-history');
    const archiveList = document.getElementById('notes-ul');
    const modalIngest = document.getElementById('modal-ingest');
    const detailPane = document.getElementById('detail-pane');
    let currentSelectedId = null;

    // 2. Archive Loading Logic (Stable Version)
    async function loadArchives() {
        if (!archiveList) return;
        archiveList.innerHTML = '<li class="loading">Syncing neural subjects...</li>';
        try {
            const response = await fetch(`${API_BASE}/graph/data`);
            const data = await response.json();
            
            archiveList.innerHTML = '';
            if (data.nodes && data.nodes.length > 0) {
                // Group nodes by Topic
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
            const response = await fetch(`${API_BASE}/archive/${currentSelectedId}`, { method: 'DELETE' });
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
        
        try {
            const response = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg })
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
        }
    }

    function appendMessage(role, text) {
        const div = document.createElement('div');
        div.className = `msg ${role}`;
        div.textContent = text;
        chatHistory.appendChild(div);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // 5. Ingestion Logic
    async function submitIngestion() {
        const btn = document.getElementById('btn-submit-ingest');
        const titleInput = document.getElementById('ingest-title');
        const contentInput = document.getElementById('ingest-content');
        const title = titleInput.value.trim();
        const content = contentInput.value.trim();

        if (!title || !content || btn.disabled) return;
        btn.disabled = true;

        try {
            const response = await fetch(`${API_BASE}/ingest`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, content })
            });
            if (response.ok) {
                modalIngest.style.display = 'none';
                titleInput.value = '';
                contentInput.value = '';
                loadArchives();
            }
        } catch (err) { console.error(err); }
        finally { btn.disabled = false; }
    }

    // 6. Event Listeners (Safe-Binding)
    const setClick = (id, fn) => {
        const el = document.getElementById(id);
        if (el) el.onclick = fn;
    };

    if (chatInput) {
        chatInput.onkeydown = (e) => {
            if (e.key === 'Enter') {
                e.preventDefault(); // 엔터 시 줄바꿈 등 기본 동작 방지
                sendMessage();
            }
        };
    }
    
    setClick('btn-ingest', () => {
        if (modalIngest) modalIngest.style.display = 'flex';
    });
    setClick('btn-cancel', () => {
        if (modalIngest) modalIngest.style.display = 'none';
    });
    setClick('btn-submit-ingest', submitIngestion);
    
    const closeBtn = document.querySelector('.btn-close-pane');
    if (closeBtn) closeBtn.onclick = hideNoteDetails;
    
    setClick('btn-delete-archive', deleteNote);

    // 7. Initialize
    loadArchives();
    async function loadChatHistory() {
        try {
            const response = await fetch(`${API_BASE}/chat/history`);
            const history = await response.json();
            if (history.length > 0) {
                chatHistory.innerHTML = '';
                history.forEach(m => appendMessage(m.role, m.content));
                const lastTopic = history[history.length - 1].topic;
                if (lastTopic) document.getElementById('topic-badge').textContent = lastTopic;
            }
        } catch (err) {}
    }
    loadChatHistory();
});
