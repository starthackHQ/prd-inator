"""
PRD-inator: Generate AI-resistant technical assignment PRDs.

Simple usage:
    >>> from prd_inator import generate_prd
    >>> from langchain_openai import ChatOpenAI
    >>> 
    >>> llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    >>> 
    >>> result = generate_prd(
    ...     role="Backend Engineer",
    ...     tech_stack="Python, FastAPI, PostgreSQL",
    ...     domain="Fintech",
    ...     seniority="Mid-level",
    ...     llm=llm
    ... )
    >>> 
    >>> print(result.candidate_prd)
    >>> print(result.evaluation_rubric)
    >>> print(result.scoring_signals)

Advanced usage with per-node LLMs:
    >>> from langchain_openai import ChatOpenAI
    >>> from langchain_anthropic import ChatAnthropic
    >>> 
    >>> default_llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    >>> adversarial_llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.9)
    >>> 
    >>> result = generate_prd(
    ...     role="Frontend Developer",
    ...     tech_stack="React, TypeScript",
    ...     domain="Healthcare",
    ...     seniority="Senior",
    ...     llm=default_llm,
    ...     node_llms={"adversarial_agent": adversarial_llm}
    ... )
"""

from typing import Dict, NamedTuple
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable
from prd_inator.graph import run_pipeline


class PRDResult(NamedTuple):
    """
    Result from PRD generation.
    
    Attributes:
        candidate_prd: The assignment document for candidates (markdown format)
        evaluation_rubric: The scoring rubric for interviewers (markdown format)
        scoring_signals: Hidden traps and evaluation signals for interviewers (markdown format)
        raw_state: Complete pipeline state (for debugging/advanced usage)
    """
    candidate_prd: str
    evaluation_rubric: str
    scoring_signals: str
    raw_state: dict


def generate_prd(
    role: str,
    tech_stack: str,
    domain: str,
    seniority: str,
    llm: BaseChatModel | Runnable,
    node_llms: Dict[str, BaseChatModel | Runnable] | None = None
) -> PRDResult:
    """
    Generate an AI-resistant technical assignment PRD.
    
    This function runs a 9-node LangGraph pipeline that:
    1. Generates diverse project ideas through cross-domain recombination
    2. Filters out AI-solvable ideas
    3. Injects realistic constraints
    4. Red-teams for vulnerabilities
    5. Patches security holes
    6. Generates evaluation rubric
    7. Produces three separate documents
    
    Args:
        role: Job role (e.g., "Backend Engineer", "Full-stack Developer")
        tech_stack: Technologies to use (e.g., "Python, FastAPI, PostgreSQL")
        domain: Business domain (e.g., "Fintech", "Healthcare", "E-commerce")
        seniority: Experience level (e.g., "Junior", "Mid-level", "Senior", "Fresher")
        llm: Pre-configured LLM instance to use for all nodes
        node_llms: Optional per-node LLM overrides, e.g., {"adversarial_agent": custom_llm}
    
    Returns:
        PRDResult: Named tuple containing:
            - candidate_prd: Assignment document (what candidates see)
            - evaluation_rubric: Scoring dimensions (interviewer-only)
            - scoring_signals: Hidden traps and signals (interviewer-only)
            - raw_state: Complete pipeline state
    
    Raises:
        ValueError: If required fields are missing or invalid
        RuntimeError: If pipeline fails after retries
    
    Example:
        >>> from langchain_openai import ChatOpenAI
        >>> 
        >>> llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        >>> 
        >>> result = generate_prd(
        ...     role="Backend Engineer",
        ...     tech_stack="Python, FastAPI, PostgreSQL",
        ...     domain="Fintech",
        ...     seniority="Mid-level",
        ...     llm=llm
        ... )
        >>> 
        >>> # Save to files
        >>> with open("assignment.md", "w") as f:
        ...     f.write(result.candidate_prd)
        >>> 
        >>> with open("rubric.md", "w") as f:
        ...     f.write(result.evaluation_rubric)
    
    Note:
        The pipeline typically takes 2-5 minutes to complete, depending on:
        - LLM provider and model speed
        - Whether idea regeneration is needed (max 3 attempts)
        - Network latency
    """
    # Validate inputs
    if not all([role, tech_stack, domain, seniority]):
        raise ValueError("All fields (role, tech_stack, domain, seniority) are required")
    
    # Prepare employer input
    employer_input = {
        "role": role.strip(),
        "tech_stack": tech_stack.strip(),
        "domain": domain.strip(),
        "seniority": seniority.strip()
    }
    
    # Run pipeline
    result = run_pipeline(employer_input, llm=llm, node_llms=node_llms)
    
    # Return structured result
    return PRDResult(
        candidate_prd=result["candidate_prd"],
        evaluation_rubric=result["evaluation_rubric_text"],
        scoring_signals=result["scoring_signals"],
        raw_state=result
    )


__all__ = ["generate_prd", "PRDResult"]
