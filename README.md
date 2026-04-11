<img width="2000" height="640" alt="prd-inator" src="https://github.com/user-attachments/assets/72a841bb-4809-4a1c-9fa4-5108d7fcc8d3" />

An autonomous LangGraph pipeline that generates AI-resistant technical assignment PRDs. Give it a role, tech stack, and domain — it handles everything else.

## What it does

Takes a single employer input and runs it through a 9-node agentic pipeline: generating ideas, filtering out AI-solvable ones, injecting real-world constraints, red-teaming for shortcuts, and producing a structured PRD with a hidden evaluation rubric.

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv venv
uv sync
```

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

## Usage

### As a Library

```python
from prd_inator import generate_prd

result = generate_prd(
    role="Backend Engineer",
    tech_stack="Python, FastAPI, PostgreSQL",
    domain="Fintech",
    seniority="Mid-level"
)

# Access outputs
print(result.candidate_prd)        # Assignment for candidate
print(result.evaluation_rubric)    # Scoring dimensions
print(result.scoring_signals)      # Hidden traps and signals

# Save to files
with open("assignment.md", "w") as f:
    f.write(result.candidate_prd)
```

### As a CLI

```bash
uv run main.py
```

## LLM Configuration

### Default Behavior

By default, the pipeline uses environment variables:

- `LLM_PROVIDER` (default: `openai`)
- `LLM_MODEL` (default: `gpt-4o`)

### Per-Node Configuration via Environment Variables

You can configure different models for specific nodes using env vars:

```bash
# Use GPT-4o for most nodes, but GPT-4o-mini for diversity enforcement
LLM_MODEL=gpt-4o
DIVERSITY_ENFORCER_MODEL=gpt-4o-mini

# Use Claude for adversarial agent
ADVERSARIAL_AGENT_PROVIDER=anthropic
ADVERSARIAL_AGENT_MODEL=claude-3-5-sonnet-20241022
```

### Programmatic Configuration

When using as a library, you can configure LLMs programmatically:

```python
from prd_inator import run_pipeline, LLMConfig

# Option 1: Same model for all nodes
config = LLMConfig(
    default_provider="openai",
    default_model="gpt-4o"
)

# Option 2: Different models per node
config = LLMConfig(
    default_provider="openai",
    default_model="gpt-4o",
    node_configs={
        "idea_divergence": {"model": "gpt-4o"},
        "anti_ai_filter": {"model": "gpt-4o-mini"},
        "adversarial_agent": {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022"
        }
    }
)

result = run_pipeline(employer_input, llm_config=config)
```

### Available Nodes for Configuration

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

## Pipeline overview

```
Employer inputs
  → Idea divergence engine
  → Diversity enforcer
  → Anti-AI filter          ↺ loops back if ideas are too weak (max 3x)
  → Constraint injector
  → Scenario transformer
  → Adversarial agent
  → Patch node
  → Evaluation designer
  → PRD generator
  → Output
```

## Output

Each run produces:

- **Assignment PRD** — candidate-facing: narrative, problem statement, incomplete requirements, deliverables
- **Evaluation rubric** — interviewer-only: scoring dimensions, failure signals
- **Hidden traps** — edge cases and adversarial patches the candidate doesn't see

## Stack

- [LangGraph](https://github.com/langchain-ai/langgraph) — agent orchestration
- [uv](https://docs.astral.sh/uv/) — dependency management
