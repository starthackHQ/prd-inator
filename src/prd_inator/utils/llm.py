"""LLM utility functions."""
from typing import Optional, List
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm(
    provider: str,
    model: str,
    temperature: float = 0,
    tools: Optional[List] = None,
    streaming: bool = False,
    **kwargs,
) -> BaseChatModel | Runnable:
    """Get configured LLM instance."""
    
    if provider == "openai":
        llm: BaseChatModel = ChatOpenAI(
            model=model,
            temperature=temperature,
            streaming=streaming,
            **kwargs,
        )
    elif provider == "gemini":
        llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            **kwargs,
        )
    else:
        raise ValueError(f"Unknown provider: '{provider}'. Supported: openai, gemini")
    
    if tools:
        llm = llm.bind_tools(tools)
    
    return llm
