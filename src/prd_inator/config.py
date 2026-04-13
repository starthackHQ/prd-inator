"""LLM configuration management."""
from typing import Dict
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable


# Global LLM storage
_default_llm: BaseChatModel | Runnable | None = None
_node_llms: Dict[str, BaseChatModel | Runnable] = {}


def set_llms(
    default_llm: BaseChatModel | Runnable | None = None,
    node_llms: Dict[str, BaseChatModel | Runnable] | None = None
):
    """
    Set LLM instances for the pipeline.
    
    Args:
        default_llm: Single LLM to use for all nodes
        node_llms: Per-node LLM overrides, e.g., {"idea_divergence": model1, "anti_ai_filter": model2}
    """
    global _default_llm, _node_llms
    _default_llm = default_llm
    _node_llms = node_llms or {}


def get_llm(node_name: str) -> BaseChatModel | Runnable:
    """Get LLM instance for a specific node."""
    if node_name in _node_llms:
        return _node_llms[node_name]
    if _default_llm is None:
        raise RuntimeError("No LLM configured. Pass 'llm' or 'node_llms' to run_pipeline()")
    return _default_llm
