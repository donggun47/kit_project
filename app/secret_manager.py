import os
import getpass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file (fixed absolute path for app/ folder)
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(env_path)

import sys

def get_secret(key_name: str, prompt_msg: Optional[str] = None) -> str:
    """
    Retrieves a secret from environment variables or prompts the user for it.
    
    Args:
        key_name (str): The name of the environment variable.
        prompt_msg (str, optional): Custom prompt message for the user.
        
    Returns:
        str: The retrieved secret.
    """
    secret = os.getenv(key_name)
    
    if not secret:
        # Avoid hanging in non-interactive environments (e.g., Render, Docker, CI)
        if not sys.stdin.isatty():
            raise ValueError(f"CRITICAL: {key_name} is missing and environment is non-interactive.")

        if not prompt_msg:
            prompt_msg = f"Enter value for {key_name}: "
        
        # Using getpass to avoid echoing sensitive keys to the terminal
        secret = getpass.getpass(prompt_msg)
        
        if not secret:
            raise ValueError(f"CRITICAL: {key_name} is required to run this application.")
            
    return secret

# Example usage for the SMMA project:
if __name__ == "__main__":
    print("--- SMMA Secret Manager Initialization ---")
    try:
        openai_key = get_secret("OPENAI_API_KEY", "Please enter your OpenAI API Key: ")
        print(f"DEBUG: Successfully loaded OpenAI Key (Length: {len(openai_key)})")
        
        # Example of loading another key
        # pinecone_key = get_secret("PINECONE_API_KEY")
        
    except Exception as e:
        print(f"Error: {e}")
