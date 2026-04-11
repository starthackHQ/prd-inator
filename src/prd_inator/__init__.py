"""prd-inator: Autonomous LangGraph pipeline for AI-resistant PRDs."""

__version__ = "0.1.0"

from prd_inator.graph import build_graph, run_pipeline
from prd_inator.config import LLMConfig, set_llm_config

__all__ = ["build_graph", "run_pipeline", "LLMConfig", "set_llm_config"]
