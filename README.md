# SMMA (Socratic Mind-Map Archive) 2.2
### 🧠 Distraction-Free Intelligence Hub for Study Verification

**SMMA** is a professional knowledge management platform designed for deep learning and study verification. Unlike traditional note-taking apps, SMMA acts as a **Socratic Mirror**, actively challenging your recorded knowledge against objective "Ground Truth" to identify misinformation, logical gaps, and hidden connections.

---

## 🚀 Core Pillars

### 1. Socratic Mirror (Intelligent Dialogue)
- **Concept Verification**: Validates your study notes against real-time objective data via LLM-powered Socratic questioning.
- **Delta-Driven Learning**: Focuses on the "Gap" between what you think you know and the objective reality.
- **Bilingual Mastery**: Supports both English and Korean seamlessly for global learning flexibility.

### 2. Semantic Memory (Subject-Based Archive)
- **Automatic Classification**: Your notes are automatically categorized into fluid "Neural Subjects" (e.g., Quantum Physics, Macroeconomics).
- **History Retrieval**: Maintains topic-specific context, allowing the AI to recall your past realizations during a session.

### 3. Relationship Discovery
- **Analogical Linking**: Automatically identifies causal links and analogies between disparate study notes.
- **Insight Feed**: Discovered relationships are broadcast to a real-time feed, enhancing peripheral awareness of your own knowledge.

### 4. SMMA Tutor Agent (MCP Integration)
- **Advanced Context Protocol**: Implements the **Model Context Protocol (MCP)** to allow external AI agents to securely interact with the neural archive.
- **Tool-Driven Reflection**: Provides tools for LLMs to resolve knowledge paths and fetch learner profiles for personalized Socratic mirroring.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn.
- **Orchestration**: LangGraph (Socratic State Logic), LangChain.
- **Vector Store**: ChromaDB (Semantic Search & RAG).
- **Database**: SQLite (Subject & Chat Meta Persistence).
- **Frontend**: Vanilla JS (ES6+), CSS Mirror-Theme (Dark Mode / Glassmorphism).

---

## 📦 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/kit_project_SMMA.git
   cd kit_project_SMMA
   ```

2. **Setup Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   - Copy `.env.template` to `.env`.
   - Add your `OPENAI_API_KEY`.
   - Copy `app/secret_manager.py.template` to `app/secret_manager.py` (if not already present).

4. **Launch Application**:
   ```bash
   python app/main.py
   ```
   Open `http://localhost:8000` in your browser.

---

## 🛡️ Security & Privacy
- **Zero Hardcoded Secrets**: Uses a unified `secret_manager` for dynamic key retrieval.
- **Local-First Data**: All databases (`smma.db`, `chroma_db/`) remain on your local machine and are excluded from Git by default.

---

## 📝 License
This project is developed for the **KIT Project** contest. All rights reserved. 2026.
