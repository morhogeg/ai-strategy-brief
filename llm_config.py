import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

# Configure OpenRouter LLM for CrewAI using CrewAI's LLM wrapper
def get_openrouter_llm():
    return LLM(
        model="openrouter/meta-llama/llama-3.1-8b-instruct:free",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        temperature=0.7,
        max_tokens=1000
    )