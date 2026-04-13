import logging
from sqlalchemy.orm import Session
from .database import SessionLocal, get_vector_store
from .models import Archive, ChatMessage, knowledge_links
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from .graph import create_smma_graph

logger = logging.getLogger("SMMA-Services")

class SMMAService:
    @staticmethod
    def get_graph_data():
        db = SessionLocal()
        try:
            archives = db.query(Archive).all()
            nodes = []
            edges = []
            for a in archives:
                nodes.append({
                    "id": str(a.id),
                    "type": "default",
                    "data": {"label": a.title, "content": a.content[:100], "type": a.source_type},
                    "position": {"x": 100 * (a.id % 5), "y": 100 * (a.id // 5)}
                })
                for conn in a.connections:
                    edges.append({
                        "id": f"e{a.id}-{conn.id}",
                        "source": str(a.id),
                        "target": str(conn.id),
                        "animated": True,
                        "label": "related"
                    })
            return {"nodes": nodes, "edges": edges}
        finally:
            db.close()

    @staticmethod
    def ingest_data(title: str, content: str, source_type: str, api_key: str):
        db = SessionLocal()
        try:
            # 1. SQL
            new_archive = Archive(title=title, content=content, source_type=source_type)
            db.add(new_archive)
            db.commit()
            db.refresh(new_archive)
            
            # 2. Vector
            vector_store = get_vector_store(api_key)
            vector_store.add_texts(
                texts=[content],
                metadatas=[{"id": new_archive.id, "title": title}]
            )
            return new_archive.id
        finally:
            db.close()

    @staticmethod
    def chat_interaction(message: str, api_key: str):
        db = SessionLocal()
        try:
            # 1. Topic Identification
            llm = ChatOpenAI(openai_api_key=api_key, model="gpt-4o")
            topic_prompt = f"Identify the primary one-word topic for this study-related message: \"{message}\". Output ONLY the word (e.g., Physics, Marketing, Geometry)."
            topic_tag = llm.invoke(topic_prompt).content.strip()

            # 2. Save User Msg
            user_msg = ChatMessage(role="user", content=message, topic_tag=topic_tag)
            db.add(user_msg)
            db.commit()

            # 3. History Retrieval
            past_messages = db.query(ChatMessage).filter(
                ChatMessage.topic_tag == topic_tag
            ).order_by(ChatMessage.timestamp.desc()).limit(10).all()
            
            context_history = []
            for m in reversed(past_messages):
                if m.role == "user":
                    context_history.append(HumanMessage(content=m.content))
                else:
                    context_history.append(AIMessage(content=m.content))

            # 4. Invoke Graph
            graph = create_smma_graph()
            initial_state = {
                "user_input": message,
                "api_key": api_key,
                "history": context_history,
                "current_topic": topic_tag,
                "external_truth": "",
                "recalled_context": "",
                "ai_question": "",
                "user_response": message,
                "comparison_result": ""
            }
            result = graph.invoke(initial_state)
            ai_reply = result.get("ai_question")

            # 5. Save AI Msg
            ai_msg = ChatMessage(role="ai", content=ai_reply, topic_tag=topic_tag)
            db.add(ai_msg)
            db.commit()

            return {
                "question": ai_reply,
                "topic": topic_tag,
                "context_used": result.get("recalled_context"),
                "external_truth": result.get("external_truth"),
                "comparison": result.get("comparison_result")
            }
        finally:
            db.close()

    @staticmethod
    def delete_archive(archive_id: str, api_key: str):
        db = SessionLocal()
        try:
            search_id = archive_id
            try: search_id = int(archive_id)
            except ValueError: pass

            archive = db.query(Archive).filter(Archive.id == search_id).first()
            
            if api_key:
                try:
                    vector_store = get_vector_store(api_key)
                    vector_store.delete(ids=[archive_id])
                except Exception as ve:
                    logger.warning(f"Vector cleanup skipped: {ve}")

            if archive:
                db.delete(archive)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
