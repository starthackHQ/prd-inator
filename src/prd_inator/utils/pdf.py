# utils/get_llm.py
import logging
import os
from typing import Optional, List
from app.core.config import get_settings
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_deepseek import ChatDeepSeek
from langchain_anthropic import ChatAnthropic
from langchain_aws import ChatBedrockConverse

logger = logging.getLogger(__name__)
_DEBUG = os.getenv("DEBUG", "false").lower() == "true"


def get_llm(
    provider: str,
    model: str,
    temperature: float = 0,
    tools: Optional[List] = None,
    streaming: bool = False,
    **kwargs,
) -> BaseChatModel | Runnable:
    """
    Single source of truth for all LLMs.

    Bedrock now supports:
    - json_schema: Native JSON Schema (Claude 4.5+, select open-weight models)
    - function_calling: Tool-based (all other models)
    Method is auto-selected based on model capabilities.
    """
    settings = get_settings()

    try:
        if provider == "openai":
            llm: BaseChatModel = ChatOpenAI(
                model=model,
                temperature=temperature,
                streaming=streaming,
                **kwargs,
            )

        elif provider == "anthropic":
            llm = ChatAnthropic(
                model=model,
                temperature=temperature,
                **kwargs,
            )

        elif provider == "gemini":
            llm = ChatGoogleGenerativeAI(
                model=model,
                temperature=temperature,
                **kwargs,
            )

        elif provider == "deepseek":
            if model == "deepseek-reasoner":
                model = "deepseek-chat"
            llm = ChatDeepSeek(
                model=model,
                temperature=temperature,
                streaming=streaming,
                **kwargs,
            )

        elif provider == "bedrock":
            if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
                raise ValueError("AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY not configured")
            import boto3
            from botocore.config import Config

            region = settings.AWS_REGION or "us-east-1"
            bedrock_client = boto3.client(
                "bedrock-runtime",
                region_name=region,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                config=Config(
                    connect_timeout=10,
                    read_timeout=120,
                    retries={"max_attempts": 3, "mode": "standard"},
                ),
            )
            llm = ChatBedrockConverse(
                model=model,
                temperature=temperature,
                region_name=region,
                client=bedrock_client,
                bedrock_api_key=None,
                **kwargs,
            )

        else:
            raise ValueError(
                f"Unknown provider: '{provider}'. "
                f"Supported: openai, anthropic, gemini, deepseek, bedrock"
            )

    except ValueError:
        raise
    except Exception as e:
        logger.error("Failed to initialize LLM %s/%s: %s", provider, model, e)
        raise RuntimeError(f"Failed to initialize LLM {provider}/{model}") from e

    try:
        if tools:
            llm = llm.bind_tools(tools)
            if _DEBUG:
                tool_names = [getattr(t, "name", type(t).__name__) for t in tools]
                logger.debug("Bound %d tools to %s/%s: %s", len(tools), provider, model, tool_names)
    except Exception as e:
        logger.error("Failed to bind tools to LLM %s/%s: %s", provider, model, e)
        raise RuntimeError(f"Failed to bind tools to LLM {provider}/{model}") from e

    return llm