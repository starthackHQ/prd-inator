# LLM Configuration System - Summary

## Overview

The prd-inator now has a flexible LLM configuration system that allows you to:
1. **Use the same model for all nodes** (simplest)
2. **Configure different models per node** (most flexible)
3. **Read configuration from environment variables** (best for pip-installed usage)

## Current Default

**By default, all nodes use:**
- Provider: `openai` (from `LLM_PROVIDER` env var)
- Model: `gpt-4o` (from `LLM_MODEL` env var)

## Three Ways to Configure

### 1. Environment Variables (Recommended for pip install)

When someone installs via pip, they just set env vars in their `.env` file:

```bash
# Default for all nodes
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o

# Override specific nodes
ADVERSARIAL_AGENT_PROVIDER=anthropic
ADVERSARIAL_AGENT_MODEL=claude-3-5-sonnet-20241022
DIVERSITY_ENFORCER_MODEL=gpt-4o-mini
```

Then in their code:
```python
from prd_inator import run_pipeline

# Automatically picks up env vars
result = run_pipeline(employer_input)
```

### 2. Programmatic Configuration (For library users)

```python
from prd_inator import run_pipeline, LLMConfig

# Same model everywhere
config = LLMConfig(
    default_provider="openai",
    default_model="gpt-4o"
)

# Or mix and match
config = LLMConfig(
    default_provider="openai",
    default_model="gpt-4o",
    node_configs={
        "adversarial_agent": {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022"
        },
        "diversity_enforcer": {"model": "gpt-4o-mini"}
    }
)

result = run_pipeline(employer_input, llm_config=config)
```

### 3. CLI Usage (main.py)

Users running `uv run main.py` can:
- Set env vars in `.env` (automatic)
- Or uncomment the config examples in `main.py` to override

## How It Works

1. **`config.py`** - Contains `LLMConfig` class that:
   - Reads default from env vars (`LLM_PROVIDER`, `LLM_MODEL`)
   - Reads per-node overrides from env vars (`NODENAME_PROVIDER`, `NODENAME_MODEL`)
   - Accepts programmatic overrides via constructor
   - Provides `get_config(node_name)` to retrieve config for each node

2. **`node.py`** - Each node calls:
   ```python
   config = get_llm_config().get_config("node_name")
   llm = get_llm(provider=config["provider"], model=config["model"], ...)
   ```

3. **`graph.py`** - `run_pipeline()` accepts optional `llm_config` parameter:
   ```python
   def run_pipeline(employer_input, llm_config=None):
       if llm_config:
           set_llm_config(llm_config)
       # ... rest of pipeline
   ```

## Node Names for Configuration

- `idea_divergence`
- `diversity_enforcer`
- `anti_ai_filter`
- `constraint_injector`
- `scenario_transformer`
- `adversarial_agent`
- `patch_node`
- `evaluation_designer`
- `self_critique`
- `prd_generator`

## Example: Cost Optimization

Use cheaper models for simple tasks:

```bash
# .env
LLM_MODEL=gpt-4o                          # Default: expensive but good
DIVERSITY_ENFORCER_MODEL=gpt-4o-mini      # Simple filtering task
ANTI_AI_FILTER_MODEL=gpt-4o-mini          # Scoring task
ADVERSARIAL_AGENT_MODEL=gpt-4o            # Keep expensive for creativity
```

## Example: Multi-Provider Setup

Use different providers for different strengths:

```bash
# .env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o

# Use Claude for adversarial thinking
ADVERSARIAL_AGENT_PROVIDER=anthropic
ADVERSARIAL_AGENT_MODEL=claude-3-5-sonnet-20241022

# Use GPT-4o-mini for simple tasks
DIVERSITY_ENFORCER_MODEL=gpt-4o-mini
```

## Files Modified

1. **`src/prd_inator/config.py`** - New file with LLMConfig class
2. **`src/prd_inator/node.py`** - All nodes now use `get_llm_config()`
3. **`src/prd_inator/graph.py`** - `run_pipeline()` accepts `llm_config` param
4. **`src/prd_inator/__init__.py`** - Exports `LLMConfig` and `set_llm_config`
5. **`main.py`** - Shows configuration examples
6. **`.env.example`** - Documents all env var options
7. **`README.md`** - Added LLM Configuration section

## For Future pip Users

When someone does `pip install prd-inator`, they can:

1. Create a `.env` file with their API keys and model preferences
2. Import and use:
   ```python
   from prd_inator import run_pipeline
   from dotenv import load_dotenv
   
   load_dotenv()
   result = run_pipeline(employer_input)
   ```

The library automatically picks up their env vars. No code changes needed!
