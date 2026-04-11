"""
PRD-inator: Generate AI-resistant technical assignment PRDs.

Simple usage:
    >>> from prd_inator import generate_prd
    >>> 
    >>> result = generate_prd(
    ...     role="Backend Engineer",
    ...     tech_stack="Python, FastAPI, PostgreSQL",
    ...     domain="Fintech",
    ...     seniority="Mid-level"
    ... )
    >>> 
    >>> print(result.candidate_prd)
    >>> print(result.evaluation_rubric)
    >>> print(result.scoring_signals)

Advanced usage with custom LLM config:
    >>> from prd_inator import generate_prd, LLMConfig
    >>> 
    >>> config = LLMConfig(
    ...     default_provider="openai",
    ...     default_model="gpt-4o",
    ...     node_configs={
    ...         "adversarial_agent": {"provider": "anthropic", "model": "claude-3-5-sonnet"}
    ...     }
    ... )
    >>> 
    >>> result = generate_prd(
    ...     role="Frontend Developer",
    ...     tech_stack="React, TypeScript",
    ...     domain="Healthcare",
    ...     seniority="Senior",
    ...     llm_config=config
    ... )
"""

from typing import Optional, NamedTuple
from prd_inator.graph import run_pipeline
from prd_inator.config import LLMConfig, set_llm_config


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
    llm_config: Optional[LLMConfig] = None
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
        llm_config: Optional LLM configuration. If not provided, reads from environment variables:
                   - LLM_PROVIDER (default: "openai")
                   - LLM_MODEL (default: "gpt-4o")
                   - Per-node overrides: {NODE_NAME}_PROVIDER, {NODE_NAME}_MODEL
    
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
        >>> result = generate_prd(
        ...     role="Backend Engineer",
        ...     tech_stack="Python, FastAPI, PostgreSQL",
        ...     domain="Fintech",
        ...     seniority="Mid-level"
        ... )
        >>> 
        >>> # Save to files
        >>> with open("assignment.md", "w") as f:
        ...     f.write(result.candidate_prd)
        >>> 
        >>> with open("rubric.md", "w") as f:
        ...     f.write(result.evaluation_rubric)
    
    Environment Variables:
        Required:
            - OPENAI_API_KEY or GOOGLE_API_KEY (depending on provider)
        
        Optional:
            - DEBUG: Set to "true" for verbose logging
            - LLM_PROVIDER: Default provider ("openai" or "gemini")
            - LLM_MODEL: Default model name
            - {NODE}_PROVIDER: Override provider for specific node
            - {NODE}_MODEL: Override model for specific node
    
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
    result = run_pipeline(employer_input, llm_config=llm_config)
    
    # Return structured result
    return PRDResult(
        candidate_prd=result["candidate_prd"],
        evaluation_rubric=result["evaluation_rubric_text"],
        scoring_signals=result["scoring_signals"],
        raw_state=result
    )


__all__ = ["generate_prd", "PRDResult", "LLMConfig"]
