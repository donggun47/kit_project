from sqlalchemy.orm import Session
from .database import SessionLocal, get_vector_store
from .models import Archive, knowledge_links
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
import logging

logger = logging.getLogger("SMMA-Consolidation")

def discover_relationships(api_key: str):
    """
    Analyzes the existing knowledge base for hidden connections 
    and updates the graph structure.
    """
    db = SessionLocal()
    try:
        archives = db.query(Archive).all()
        if len(archives) < 2:
            return {"status": "skipped", "reason": "Not enough archives for comparison."}

        llm = ChatOpenAI(model="gpt-4o", openai_api_key=api_key)
        
        # We'll use a Socratic prompt to find bridges
        prompt = ChatPromptTemplate.from_template("""
        You are a Knowledge Consolidation Expert. 
        Compare these two study notes and determine if there is a semantic connection.
        
        Note A: {title_a} - {content_a}
        Note B: {title_b} - {content_b}
        
        If there is a connection, specify the type (analogy, causality, prerequisite, contradiction) 
        and a brief reason why. If no connection, return 'NONE'.
        
        Format: Type: [type] | Reason: [reason]
        """)

        new_links_count = 0

        # O(n^2) comparison - for larger scale, we would use Vector search first
        for i in range(len(archives)):
            for j in range(i + 1, len(archives)):
                a1 = archives[i]
                a2 = archives[j]
                
                # Check if link already exists
                existing = db.execute(
                    knowledge_links.select().where(
                        ((knowledge_links.c.source_archive_id == a1.id) & (knowledge_links.c.target_archive_id == a2.id)) |
                        ((knowledge_links.c.source_archive_id == a2.id) & (knowledge_links.c.target_archive_id == a1.id))
                    )
                ).first()
                
                if existing:
                    continue

                # Ask LLM to find connection
                chain = prompt | llm
                response = chain.invoke({
                    "title_a": a1.title, "content_a": a1.content,
                    "title_b": a2.title, "content_b": a2.content
                })
                
                res_text = response.content.upper()
                if "NONE" not in res_text and "TYPE:" in res_text:
                    # Parse type
                    try:
                        rel_type = res_text.split("TYPE:")[1].split("|")[0].strip()
                        # Add link
                        ins = knowledge_links.insert().values(
                            source_archive_id=a1.id,
                            target_archive_id=a2.id,
                            relationship_type=rel_type,
                            strength=1
                        )
                        db.execute(ins)
                        new_links_count += 1
                        logger.info(f"Discovered link: {a1.title} <-> {a2.title} ({rel_type})")
                    except Exception as e:
                        logger.error(f"Error parsing link: {e}")

        db.commit()
        return {"status": "success", "new_links": new_links_count}
        
    except Exception as e:
        logger.error(f"Consolidation error: {e}")
        return {"status": "error", "detail": str(e)}
    finally:
        db.close()
 
