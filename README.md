# prd-inator

An autonomous LangGraph pipeline that generates AI-resistant technical assignment PRDs. Give it a role, tech stack, and domain — it handles everything else.

## What it does

Takes a single employer input and runs it through an 11-node agentic pipeline: generating ideas, filtering out AI-solvable ones, injecting real-world constraints, red-teaming for shortcuts, and producing a structured PRD with a hidden evaluation rubric.

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv venv
uv sync
```

## Usage

```bash
uv run main.py
```

## Pipeline overview

```
Employer inputs
  → Idea divergence engine
  → Diversity enforcer
  → Anti-AI filter          ↺ loops back if ideas are too weak
  → Constraint injector
  → Scenario transformer
  → Adversarial agent
  → Patch node
  → Evaluation designer
  → Self-critique loop      ↺ loops back if assignment is still generic
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