
import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()


def get_llm():
    model = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

    return ChatOllama(
        model=model,
        temperature=0.2,
        verbose = True,
        num_predict=1500,
        base_url="http://localhost:11434",
    )
