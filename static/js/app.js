document.addEventListener('DOMContentLoaded', () => {
    // 1. Core State
    const API_BASE = ""; 
    const chatInput = document.getElementById('chat-input');
    const chatHistory = document.getElementById('chat-history');
    const archiveList = document.getElementById('notes-ul');
    const modalIngest = document.getElementById('modal-ingest');
    const modalSettings = document.getElementById('modal-settings');
    const titleIn = document.getElementById('ingest-title');
    const contentIn = document.getElementById('ingest-content');
    const detailPane = document.getElementById('detail-pane');
    const sysStatus = document.getElementById('system-status');
    let currentSelectedId = null;

    // 1-1. Neural Credentials Management (LocalStorage)
    const getNeuralConfig = () => ({
        openai: localStorage.getItem('smma_openai_key') || "",
        pinecone: localStorage.getItem('smma_pinecone_key') || "",
        index: localStorage.getItem('smma_pinecone_index') || "smma-brains"
    });

    const saveNeuralConfig = (openai, pinecone, index) => {
        localStorage.setItem('smma_openai_key', openai);
        localStorage.setItem('smma_pinecone_key', pinecone);
        localStorage.setItem('smma_pinecone_index', index);
        alert("Neural configuration updated successfully.");
        if (modalSettings) modalSettings.style.display = 'none';
    };

    // Initialize Settings Inputs
    const setOpenAI = document.getElementById('setting-openai-key');
    const setPinecone = document.getElementById('setting-pinecone-key');
    const setIndex = document.getElementById('setting-pinecone-index');
    
    const config = getNeuralConfig();
    if(setOpenAI) setOpenAI.value = config.openai;
    if(setPinecone) setPinecone.value = config.pinecone;
    if(setIndex) setIndex.value = config.index;

    // 2. Archive Loading Logic
    async function loadArchives() {
        if (!archiveList) return;
        archiveList.innerHTML = '<li class="loading">Syncing neural subjects...</li>';
        try {
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
        const dT = document.getElementById('detail-title');
        const dTy = document.getElementById('detail-type');
        const dID = document.getElementById('detail-id');
        const dC = document.getElementById('detail-content');
        if(dT) dT.textContent = data.label;
        if(dTy) dTy.textContent = data.type || 'study';
        if(dID) dID.textContent = id;
        if(dC) dC.textContent = data.content || 'No content available.';
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

    // 4. Chat Logic
    async function sendMessage() {
        const msg = chatInput.value.trim();
        if (!msg) return;

        appendMessage('user', msg);
        chatInput.value = '';
        if (sysStatus) sysStatus.textContent = "Socrates is thinking...";
        
        const conf = getNeuralConfig();

        try {
            const response = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: msg,
                    openai_api_key: conf.openai,
                    pinecone_api_key: conf.pinecone,
                    pinecone_index: conf.index
                }),
                cache: 'no-store'
            });

            if (response.ok) {
                const data = await response.json();
                appendMessage('ai', data.question);
                const badge = document.getElementById('topic-badge');
                if (data.topic && badge) badge.textContent = data.topic;
            } else {
                const err = await response.json();
                let msg = err.detail || "Check API Keys";
                if (msg.includes("not found") || msg.includes("NOT_FOUND")) {
                    msg = "Neural Index is being initialized. Please wait ~60 seconds and try again.";
                }
                appendMessage('ai', `Neural link interrupted: ${msg}`);
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
        if(chatHistory) {
            chatHistory.appendChild(div);
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }
    }

    // 5. Ingestion Logic (Enhanced with Cooldown & Global Guard)
    let isIngesting = false;
    let lastSubmitTime = 0;
    async function submitIngestion() {
        // 1. Mandatory Cooldown (1 second) to prevent hyper-fast double fire
        const now = Date.now();
        if (now - lastSubmitTime < 1000) return;
        
        const btn = document.getElementById('btn-submit-ingest');
        const titleInput = document.getElementById('ingest-title');
        const contentInput = document.getElementById('ingest-content');
        
        if (!titleInput || !contentInput) return;
        
        const title = titleInput.value.trim();
        const content = contentInput.value.trim();

        // 2. Global Guard Check
        if (!title || !content || isIngesting || (btn && btn.disabled)) return;
        
        // 3. Lock immediately
        isIngesting = true;
        lastSubmitTime = now;
        
        const conf = getNeuralConfig();
        const originalText = btn ? btn.textContent : "Sync";
        if(btn) {
            btn.disabled = true;
            btn.textContent = "Syncing...";
        }

        try {
            const response = await fetch(`${API_BASE}/ingest`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    title, 
                    content,
                    openai_api_key: conf.openai,
                    pinecone_api_key: conf.pinecone,
                    pinecone_index: conf.index
                }),
                cache: 'no-store'
            });

            if (response.ok) {
                if (modalIngest) modalIngest.style.display = 'none';
                titleInput.value = '';
                contentInput.value = '';
                await loadArchives();
            } else {
                const errorData = await response.json();
                alert("Archive Sync Failed: " + (errorData.detail || "Check API Keys"));
            }
        } catch (err) { 
            console.error(err);
            alert("Neural connection error during sync.");
        } finally { 
            // We keep isIngesting true for a short moment extra to be safe
            setTimeout(() => {
                isIngesting = false;
                if (btn) {
                    btn.disabled = false; 
                    btn.textContent = originalText;
                }
            }, 500);
        }
    }

    // 6. Event Listeners
    const setClick = (id, fn) => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('click', fn);
    };

    // Ingest Shortcuts
    if (titleIn) titleIn.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); submitIngestion(); } });
    if (contentIn) contentIn.addEventListener('keydown', e => { if (e.key === 'Enter' && e.ctrlKey) { e.preventDefault(); submitIngestion(); } });

    // Chat Shortcuts
    if (chatInput) chatInput.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); sendMessage(); } });

    // Modals
    setClick('btn-ingest', () => { if (modalIngest) { modalIngest.style.display = 'flex'; if (titleIn) titleIn.focus(); } });
    setClick('btn-cancel', () => { if (modalIngest) modalIngest.style.display = 'none'; });
    setClick('btn-submit-ingest', submitIngestion);

    // Settings Modal
    setClick('btn-settings', () => { if (modalSettings) modalSettings.style.display = 'flex'; });
    setClick('btn-settings-cancel', () => { if (modalSettings) modalSettings.style.display = 'none'; });
    setClick('btn-settings-save', () => {
        saveNeuralConfig(setOpenAI.value, setPinecone.value, setIndex.value);
    });

    const closeBtn = document.querySelector('.btn-close-pane');
    if (closeBtn) closeBtn.addEventListener('click', hideNoteDetails);
    setClick('btn-delete-archive', deleteNote);

    // 7. Initialize
    loadArchives();
    async function loadChatHistory() {
        try {
            const response = await fetch(`${API_BASE}/chat/history`, { cache: 'no-store' });
            const history = await response.json();
            if (history.length > 0 && chatHistory) {
                chatHistory.innerHTML = '';
                history.forEach(m => appendMessage(m.role, m.content));
            }
        } catch (err) {}
    }
    loadChatHistory();
});
