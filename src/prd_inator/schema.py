"""Data schemas and models."""
from typing import List, Dict
from pydantic import BaseModel, Field


class Idea(BaseModel):
    """Single project idea."""
    title: str = Field(description="Project title")
    description: str = Field(description="2-3 sentence description")


class IdeaList(BaseModel):
    """List of project ideas."""
    ideas: List[Idea] = Field(description="List of project ideas")


class AntiAIScore(BaseModel):
    """Scoring for anti-AI filter."""
    idea_title: str
    gpt_solvable_score: int = Field(ge=0, le=3, description="0=hard, 3=trivial for GPT")
    template_score: int = Field(ge=0, le=3, description="0=novel, 3=boilerplate")
    googleable_score: int = Field(ge=0, le=3, description="0=unique, 3=common")
    total_score: int = Field(description="Sum of all scores")
    reasoning: str


class AntiAIScores(BaseModel):
    """Scores for all ideas."""
    scores: List[AntiAIScore]


class Constraints(BaseModel):
    """Injected constraints."""
    incomplete_requirement: str
    conflicting_goal: str
    scaling_edge_case: str
    failure_condition: str


class Vulnerability(BaseModel):
    """Single vulnerability found by adversarial agent."""
    exploit_type: str = Field(description="Type of shortcut (AI, hardcode, etc)")
    description: str = Field(description="How to exploit this weakness")


class Vulnerabilities(BaseModel):
    """List of vulnerabilities."""
    vulnerabilities: List[Vulnerability]


class CoreRequirement(BaseModel):
    """Single core requirement."""
    summary: str = Field(description="One-line requirement summary")
    details: List[str] = Field(description="2-3 key details", max_length=3)


class FunctionalComponent(BaseModel):
    """Functional component with interface details."""
    component_name: str
    interface: str = Field(description="API endpoint or interface signature")
    details: List[str] = Field(description="3-5 implementation details", max_length=5)


class NonFunctionalRequirement(BaseModel):
    """Non-functional requirements by category."""
    performance: List[str] = Field(max_length=2)
    resilience: List[str] = Field(max_length=2)
    security: List[str] = Field(max_length=2)
    developer_experience: List[str] = Field(max_length=2)


class StructuredScenario(BaseModel):
    """Structured scenario output from scenario_transformer."""
    objective_context: str = Field(description="2-3 sentences on business problem and what to build")
    product_value: List[str] = Field(description="3-4 benefit bullets", min_length=3, max_length=4)
    core_requirements: List[CoreRequirement] = Field(description="3-5 requirements", min_length=3, max_length=5)
    functional_components: List[FunctionalComponent] = Field(description="2-3 components", max_length=3)
    non_functional_requirements: NonFunctionalRequirement
    user_flow: List[str] = Field(description="5-6 step flow", min_length=5, max_length=6)


class CandidatePRD(BaseModel):
    """Structured candidate-facing PRD."""
    objective_context: str
    product_value: List[str]
    tech_stack: List[str]
    core_requirements: List[CoreRequirement]
    functional_requirements: List[FunctionalComponent]
    non_functional_requirements: NonFunctionalRequirement
    user_flow: List[str]


class FinalPRD(BaseModel):
    """Final structured PRD output."""
    candidate_prd: CandidatePRD = Field(description="Structured candidate-facing assignment")
