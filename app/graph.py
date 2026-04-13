from typing import Annotated, List, TypedDict, Union
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from .database import get_vector_store
import os

# --- State Definition ---
class SMMAState(TypedDict):
    """The state of the Socratic Mirroring graph."""
    user_input: str
    external_truth: str  # Objective baseline
    recalled_context: str # User's subjective archives
    ai_question: str      # The Socratic Mirror output
    user_response: str
    comparison_result: str
    history: List[BaseMessage]
    current_topic: str # Subject-based memory tag
    api_key: str

# --- Node Implementation ---

def external_check_node(state: SMMAState):
    """Fetches objective facts about the user's topic for ground truth."""
    llm = ChatOpenAI(openai_api_key=state['api_key'], model="gpt-4o")
    prompt = f"""
    Explain the objective, factual definition of the following concept: "{state['user_input']}"
    Provide a concise, neutral, and accurate summary.
    If the user's query is in Korean, respond in Korean.
    """
    response = llm.invoke(prompt)
    return {"external_truth": response.content}

def recall_node(state: SMMAState):
    """Retrieves relevant user memories from the Vector DB."""
    vector_store = get_vector_store(state['api_key'])
    docs = vector_store.similarity_search(state['user_input'], k=3)
    context = "\n".join([d.page_content for d in docs])
    
    if not context:
        context = "No specific past records found for this topic."
        
    return {"recalled_context": context}

def mirroring_node(state: SMMAState):
    """Generates a mirroring question by triangulating external truth vs internal memory."""
    llm = ChatOpenAI(openai_api_key=state['api_key'], model="gpt-4o")
    
    prompt = f"""
    You are an AI Tutor using Socratic Mirroring. You are currently discussing the topic: "{state.get('current_topic', 'General Learning')}".
    
    CONVERSATION HISTORY (Last 10 turns for this topic):
    {state['history']}

    GROUND TRUTH (External):
    {state['external_truth']}
    
    USER'S MEMORY (Internal Archives):
    {state['recalled_context']}
    
    CURRENT CONTEXT: "{state['user_input']}"
    
    TASK: 
    1. Compare the user's internal memory with the objective ground truth.
    2. Refer to the CONVERSATION HISTORY to ensure the dialogue flows naturally.
    3. If there is a contradiction (Misinformation), ask a subtle question that highlights the gap.
    4. If they align, ask a question that pushes the user to deeper connections.
    5. NEVER just give the answer. Use the delta between archives and truth to guide them.
    6. MANDATORY: You must respond in the same language as the user's input (e.g., if the user writes in Korean, you MUST respond in Korean).
    """
    response = llm.invoke(prompt)
    return {"ai_question": response.content}

def reconciliation_node(state: SMMAState):
    """Final check to ensure user's new output aligns with truth or archives."""
    llm = ChatOpenAI(openai_api_key=state['api_key'], model="gpt-4o")
    
    prompt = f"""
    The user responds: "{state['user_response']}"
    Original Archives: "{state['recalled_context']}"
    External Truth: "{state['external_truth']}"
    
    Assess if the user has successfully bridged the gap or corrected any previous misinformation.
    """
    response = llm.invoke(prompt)
    return {"comparison_result": response.content}

# --- Graph Assembly ---

def create_smma_graph():
    workflow = StateGraph(SMMAState)
    
    # Add Nodes
    workflow.add_node("external_check", external_check_node)
    workflow.add_node("recall", recall_node)
    workflow.add_node("mirror", mirroring_node)
    workflow.add_node("reconcile", reconciliation_node)
    
    # Define Edges: External First -> Internal Second
    workflow.set_entry_point("external_check")
    workflow.add_edge("external_check", "recall")
    workflow.add_edge("recall", "mirror")
    workflow.add_edge("mirror", "reconcile")
    workflow.add_edge("reconcile", END)
    
    return workflow.compile()

# Utility to visualize graph (as Mermaid)
def get_graph_visualization():
    graph = create_smma_graph()
    return graph.get_graph().draw_mermaid()
