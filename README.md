<img src="https://github.com/user-attachments/assets/72a841bb-4809-4a1c-9fa4-5108d7fcc8d3" alt="PRDinator" width="100%" />
<br />
<p align="center">
An autonomous LangGraph pipeline that generates AI-resistant technical assignment PRDs. Give it a role, tech stack, and domain — it handles everything else.
</p>

## What it does

Takes a single employer input and runs it through an 8-node agentic pipeline: generating ideas, filtering out AI-solvable ones, injecting real-world constraints, red-teaming for shortcuts, and producing a structured PRD.
```
pip install prd-inator
```

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
from langchain_openai import ChatOpenAI

# Initialize your LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

result = generate_prd(
    role="Backend Engineer",
    tech_stack="Python, FastAPI, PostgreSQL",
    domain="Fintech",
    seniority="Mid-level",
    llm=llm
)

# Access output
print(result.candidate_prd)  # Assignment for candidate

# Save to file
with open("assignment.md", "w") as f:
    f.write(result.candidate_prd)
```

### As a CLI

```bash
uv run main.py
```

## LLM Configuration

### Simple: Single LLM for All Nodes

Pass a pre-configured LLM instance to use for all pipeline nodes:

```python
from langchain_openai import ChatOpenAI
from prd_inator import generate_prd

llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

result = generate_prd(
    role="Backend Engineer",
    tech_stack="Python, FastAPI, PostgreSQL",
    domain="Fintech",
    seniority="Mid-level",
    llm=llm
)
```

### Advanced: Per-Node LLM Configuration

Use different LLMs for specific nodes:

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from prd_inator import generate_prd

# Default LLM for most nodes
default_llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# Use Claude for adversarial thinking
adversarial_llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.9)

# Use cheaper model for diversity enforcement
cheap_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

result = generate_prd(
    role="Frontend Developer",
    tech_stack="React, TypeScript",
    domain="Healthcare",
    seniority="Senior",
    llm=default_llm,
    node_llms={
        "adversarial_agent": adversarial_llm,
        "diversity_enforcer": cheap_llm
    }
)
```

### Why This Approach?

- **Bring your own LLM**: Use any LangChain-compatible model (OpenAI, Anthropic, local models, custom wrappers)
- **Full control**: Configure temperature, max_tokens, timeouts, retries, etc.
- **No coupling**: The library doesn't manage API keys or provider initialization
- **Flexible**: Mix and match models per node for cost/quality optimization

### Available Nodes for Configuration

- `idea_divergence`
- `diversity_enforcer`
- `anti_ai_filter`
- `constraint_injector`
- `scenario_transformer`
- `adversarial_agent`
- `patch_node`
- `prd_generator`

## Pipeline overview

```
Employer inputs
  → Idea divergence engine
  → Diversity enforcer
  → Anti-AI filter          ↺ loops back if ideas are too weak (max 3x)
  → Constraint injector
  → Scenario transformer    (generates structured PRD components)
  → Adversarial agent
  → Patch node              (hardens PRD against shortcuts)
  → PRD generator           (assembles final document)
  → Output
```

## Output

Each run produces a single structured PRD document with:

- **Objective & Context** — business problem and what to build
- **Technical Stack** — required technologies
- **Core Requirements** — 3-5 main requirements with details
- **Functional Requirements** — API endpoints/interfaces with specifications
- **Non-Functional Requirements** — performance, resilience, security, developer experience
- **User Flow** — end-to-end step-by-step flow

## Stack

- [LangGraph](https://github.com/langchain-ai/langgraph) — agent orchestration
- [uv](https://docs.astral.sh/uv/) — dependency management
