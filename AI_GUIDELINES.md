# AI Collaboration Guidelines for SMMA

## 1. Core Mission
The mission of this project is to build the **Semantic Mind-Map Archive (SMMA)**, an AI-powered education solution that solves the "pain point" of managing and retrieving study files using RAG (Retrieval-Augmented Generation) and Semantic Search.

## 2. Mandatory Logging Rule
An AI activity log must be maintained in `ai_report_log.md` at all times.
- **Language:** English.
- **When to log:** Every session, major code change, architectural decision, or bug fix.
- **Format:** Include Timestamp, Task, Decisions, and Outcome.
- **Purpose:** This log will be used to generate the final "AI Report" for the contest.

## 3. Security & Privacy (CRITICAL)
- **NO HARDCODED SECRETS:** Never store API keys, passwords, or personal information directly in the code.
- **Credential Management:** 
  - Use `secret_manager.py` for all credential access.
  - API keys must be provided via input at runtime or through a git-ignored `.env` file.
  - Check `secret_manager.py` before adding any new external service integration.

## 4. Technical Stack
- **Frontend:** Next.js (Responsive)
- **Backend:** FastAPI
- **AI:** LangChain, OpenAI (or similar LLMs), Vector DB (Pinecone/Chroma)
- **Database:** PostgreSQL (for relational data)

## 5. Development Principles
- **Aesthetic Excellence:** UI should be premium, using modern typography and smooth interactions.
- **User-Centric:** Focus on solving the "where did I save this?" problem.
- **Context-Aware:** Every tool or feature should understand the user's study context.
