"""Graph state definitions."""
from typing import TypedDict, List, Dict, Any, Annotated


class GraphState(TypedDict):
    """State object passed through the LangGraph pipeline."""
    
    # Input
    employer_input: Dict[str, str]  # role, stack, domain, seniority
    
    # Idea generation phase
    ideas: List[Dict[str, str]]  # raw ideas from divergence engine
    filtered_ideas: List[Dict[str, str]]  # after diversity enforcement
    selected_idea: Dict[str, Any]  # top scorer after anti-AI filter
    idea_loop_count: Annotated[int, lambda x, y: y]  # Always replace, don't add
    
    # Constraint and scenario phase
    constraints: List[str]  # injected constraints, patched later
    scenario: str  # narrative scenario, patched later
    
    # Adversarial phase
    vulnerabilities: List[Dict[str, str]]  # from adversarial agent
    
    # Evaluation phase
    evaluation_rubric: Dict[str, Any]  # scoring dimensions
    
    # Output
    candidate_prd: str  # candidate-facing PRD
    evaluation_rubric_text: str  # interviewer rubric
    scoring_signals: str  # interviewer scoring signals
