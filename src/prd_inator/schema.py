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


class ScoringDimension(BaseModel):
    """Single scoring dimension in rubric."""
    name: str
    weight: float = Field(ge=0, le=1)
    excellent: str = Field(description="What 4-5 looks like")
    passing: str = Field(description="What 2-3 looks like")
    failure: str = Field(description="What 0-1 looks like")


class EvaluationRubric(BaseModel):
    """Complete evaluation rubric."""
    dimensions: List[ScoringDimension]


class FinalPRD(BaseModel):
    """Final structured PRD output."""
    candidate_prd: str = Field(description="Candidate-facing assignment document")
    evaluation_rubric: str = Field(description="Interviewer-only evaluation rubric")
    scoring_signals: str = Field(description="Interviewer-only scoring signals and hidden traps")
