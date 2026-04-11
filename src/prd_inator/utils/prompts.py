"""Prompt template loader utility."""
import yaml
from pathlib import Path


def load_prompts():
    """Load all prompts from prompts.yml."""
    prompts_path = Path(__file__).parent.parent / "prompts.yml"
    with open(prompts_path, 'r') as f:
        return yaml.safe_load(f)


def get_prompt(prompt_name: str) -> str:
    """Get a specific prompt by name."""
    prompts = load_prompts()
    return prompts.get(prompt_name, "")
