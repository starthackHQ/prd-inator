"""LLM configuration management."""
import os
from typing import Optional, Dict


class LLMConfig:
    """Configuration for LLM models used in the pipeline."""
    
    def __init__(
        self,
        default_provider: Optional[str] = None,
        default_model: Optional[str] = None,
        node_configs: Optional[Dict[str, Dict[str, str]]] = None
    ):
        """
        Initialize LLM configuration.
        
        Args:
            default_provider: Default LLM provider (e.g., "openai", "anthropic")
            default_model: Default model name (e.g., "gpt-4o", "claude-3-5-sonnet-20241022")
            node_configs: Per-node overrides, e.g., {"idea_divergence": {"model": "gpt-4o-mini"}}
        """
        # Read from env vars if not provided
        self.default_provider = default_provider or os.getenv("LLM_PROVIDER", "openai")
        self.default_model = default_model or os.getenv("LLM_MODEL", "gpt-4o")
        self.node_configs = node_configs or {}
        
        # Load per-node configs from env vars (format: NODE_NAME_PROVIDER, NODE_NAME_MODEL)
        self._load_node_configs_from_env()
    
    def _load_node_configs_from_env(self):
        """Load per-node configurations from environment variables."""
        node_names = [
            "idea_divergence", "diversity_enforcer", "anti_ai_filter",
            "constraint_injector", "scenario_transformer", "adversarial_agent",
            "patch_node", "evaluation_designer", "self_critique", "prd_generator"
        ]
        
        for node in node_names:
            env_prefix = node.upper()
            provider = os.getenv(f"{env_prefix}_PROVIDER")
            model = os.getenv(f"{env_prefix}_MODEL")
            
            if provider or model:
                if node not in self.node_configs:
                    self.node_configs[node] = {}
                if provider:
                    self.node_configs[node]["provider"] = provider
                if model:
                    self.node_configs[node]["model"] = model
    
    def get_config(self, node_name: str) -> Dict[str, str]:
        """
        Get LLM configuration for a specific node.
        
        Args:
            node_name: Name of the node
            
        Returns:
            Dict with "provider" and "model" keys
        """
        node_config = self.node_configs.get(node_name, {})
        
        return {
            "provider": node_config.get("provider", self.default_provider),
            "model": node_config.get("model", self.default_model)
        }


# Global config instance
_llm_config: Optional[LLMConfig] = None


def set_llm_config(config: LLMConfig):
    """Set the global LLM configuration."""
    global _llm_config
    _llm_config = config


def get_llm_config() -> LLMConfig:
    """Get the global LLM configuration, creating default if needed."""
    global _llm_config
    if _llm_config is None:
        _llm_config = LLMConfig()
    return _llm_config
