from fastmcp import FastMCP
import os
from dotenv import load_dotenv
from .secret_manager import get_secret

# --- Configuration & Context ---
# Load environment variables for local testing
load_dotenv()

# Create a professional MCP server for the SMMA project
mcp = FastMCP("SMMA-Tutor-Agent")

@mcp.tool()
def get_llm_config() -> str:
    """Returns the current model configuration for the Socratic Mirror."""
    return "Model: GPT-4o | Framework: LangGraph v1.1 | Strategy: Socratic Mirroring"

@mcp.tool()
def get_learner_profile() -> str:
    """
    Returns a generic learner profile to guide the Socratic Mirror's tone.
    (Personal identity stripped for public security)
    """
    return (
        "Role: Dedicated Student / AI Engineering Learner\n"
        "Goal: Deep understanding through study verification and error correction.\n"
        "Preferred Tone: Encouraging, challenging, and strictly Socratic."
    )

@mcp.tool()
def resolve_knowledge_path(alias: str) -> str:
    """
    Converts a logic alias into a relative project path for security.
    Shows how the AI maps conceptual subjects to local storage.
    """
    # Use robust relative path resolution
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path_map = {
        "archives": os.path.join(base_dir, "smma.db"),
        "embeddings": os.path.join(base_dir, "chroma_db"),
        "logs": os.path.join(base_dir, "ai_report_log.md")
    }
    return path_map.get(alias, f"Knowledge alias '{alias}' not found.")

@mcp.prompt()
def socratic_system_prompt(topic: str) -> str:
    """The core system prompt for the SMMA agent, injectable via MCP."""
    return (
        f"You are the SMMA Tutor Agent specializing in '{topic}'.\n"
        "Access the user's archives to find inconsistencies between their notes and objective truth.\n"
        "Always guide the user with questions rather than answers."
    )

if __name__ == "__main__":
    # The server runs via stdio for seamless integration with AI clients
    mcp.run()
