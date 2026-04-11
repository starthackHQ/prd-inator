"""prd-inator: Autonomous LangGraph pipeline for AI-resistant PRDs."""

__version__ = "0.1.0"

# Public API
from prd_inator.api import generate_prd, PRDResult
from prd_inator.config import LLMConfig

# For advanced users
from prd_inator.graph import build_graph, run_pipeline

__all__ = [
    # Simple API (recommended)
    "generate_prd",
    "PRDResult",
    "LLMConfig",
    
    # Advanced API
    "build_graph",
    "run_pipeline",
]
