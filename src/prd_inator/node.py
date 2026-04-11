"""Pipeline node implementations."""
from typing import Literal
from prd_inator.state import GraphState
from prd_inator.schema import (
    IdeaList, AntiAIScores, Constraints, Vulnerabilities,
    EvaluationRubric
)
from prd_inator.utils import get_llm, get_prompt, logger
from prd_inator.config import get_llm_config


def employer_input_node(state: GraphState) -> dict:
    """Validate employer inputs."""
    logger.debug("Node: employer_input - Starting...")
    required_fields = ["role", "tech_stack", "domain", "seniority"]
    employer_input = state.get("employer_input", {})
    
    for field in required_fields:
        if not employer_input.get(field):
            raise ValueError(f"Missing required field: {field}")
    
    logger.debug("Employer input validated")
    return {"idea_loop_count": 0}


def idea_divergence_engine(state: GraphState) -> dict:
    """Generate 15 diverse project ideas."""
    logger.debug("Node: idea_divergence_engine - Starting...")
    
    try:
        prompt = get_prompt("idea_divergence").format(**state["employer_input"])
        
        logger.debug(f"Prompt length: {len(prompt)} chars")
        config = get_llm_config().get_config("idea_divergence")
        logger.debug(f"Using LLM: {config['provider']}/{config['model']}")
        
        llm = get_llm(provider=config["provider"], model=config["model"], temperature=0.9)
        structured_llm = llm.with_structured_output(IdeaList)
        
        logger.debug("Calling LLM...")
        result = structured_llm.invoke(prompt)
        logger.debug(f"Got {len(result.ideas)} ideas")
        
        return {"ideas": [idea.model_dump() for idea in result.ideas]}
    
    except Exception as e:
        logger.error(f"Error in idea_divergence_engine: {e}")
        raise


def diversity_enforcer(state: GraphState) -> dict:
    """Remove semantic duplicates from ideas."""
    logger.debug("Node: diversity_enforcer - Starting...")
    
    try:
        ideas_text = "\n\n".join([
            f"{i+1}. {idea['title']}: {idea['description']}"
            for i, idea in enumerate(state["ideas"])
        ])
        
        prompt = get_prompt("diversity_enforcer").format(
            ideas=ideas_text,
            **state["employer_input"]
        )
        
        config = get_llm_config().get_config("diversity_enforcer")
        logger.debug(f"Using LLM: {config['provider']}/{config['model']}")
        
        llm = get_llm(provider=config["provider"], model=config["model"], temperature=0.3)
        structured_llm = llm.with_structured_output(IdeaList)
        
        result = structured_llm.invoke(prompt)
        logger.debug(f"Filtered to {len(result.ideas)} ideas")
        
        return {"filtered_ideas": [idea.model_dump() for idea in result.ideas]}
    
    except Exception as e:
        logger.error(f"Error in diversity_enforcer: {e}")
        raise


def anti_ai_filter(state: GraphState) -> dict:
    """Score ideas on AI-resistance and select the best."""
    logger.debug("Node: anti_ai_filter - Starting...")
    
    try:
        ideas_text = "\n\n".join([
            f"{i+1}. {idea['title']}: {idea['description']}"
            for i, idea in enumerate(state["filtered_ideas"])
        ])
        
        prompt = get_prompt("anti_ai_filter").format(
            ideas=ideas_text,
            **state["employer_input"]
        )
        
        config = get_llm_config().get_config("anti_ai_filter")
        logger.debug(f"Using LLM: {config['provider']}/{config['model']}")
        
        llm = get_llm(provider=config["provider"], model=config["model"], temperature=0.2)
        structured_llm = llm.with_structured_output(AntiAIScores)
        
        result = structured_llm.invoke(prompt)
        scores = result.scores
        
        # Filter ideas with total_score <= 5 (lower is better)
        passing_ideas = [s for s in scores if s.total_score <= 5]
        
        if len(passing_ideas) < 2:
            logger.debug("Not enough passing ideas, will regenerate")
            return {"selected_idea": {}}
        
        # Select the best (lowest score)
        best = min(passing_ideas, key=lambda x: x.total_score)
        logger.debug(f"Selected idea: {best.idea_title} (score: {best.total_score})")
        
        # Find the original idea
        for idea in state["filtered_ideas"]:
            if idea["title"] == best.idea_title:
                return {"selected_idea": idea}
        
        return {"selected_idea": {}}
    
    except Exception as e:
        logger.error(f"Error in anti_ai_filter: {e}")
        raise


def should_regenerate_ideas(state: GraphState) -> Literal["regenerate", "continue"]:
    """Conditional edge: check if we need to regenerate ideas."""
    if not state.get("selected_idea"):
        if state["idea_loop_count"] < 3:
            logger.debug(f"Regenerating ideas (attempt {state['idea_loop_count'] + 1}/3)")
            return "regenerate"
        else:
            raise RuntimeError("Failed to generate suitable ideas after 3 attempts")
    return "continue"


def constraint_injector(state: GraphState) -> dict:
    """Inject deliberate friction into the selected idea."""
    logger.debug("Node: constraint_injector - Starting...")
    
    idea_text = f"{state['selected_idea']['title']}: {state['selected_idea']['description']}"
    seniority = state["employer_input"].get("seniority", "mid-level")
    
    prompt = get_prompt("constraint_injector").format(idea=idea_text, seniority=seniority)
    
    config = get_llm_config().get_config("constraint_injector")
    logger.debug(f"Using LLM: {config['provider']}/{config['model']}")
    
    llm = get_llm(provider=config["provider"], model=config["model"], temperature=0.7)
    structured_llm = llm.with_structured_output(Constraints)
    
    result = structured_llm.invoke(prompt)
    logger.debug("Constraints injected")
    
    return {
        "constraints": [
            result.incomplete_requirement,
            result.conflicting_goal,
            result.scaling_edge_case,
            result.failure_condition
        ]
    }


def scenario_transformer(state: GraphState) -> dict:
    """Convert idea into grounded narrative scenario."""
    logger.debug("Node: scenario_transformer - Starting...")
    
    idea_text = f"{state['selected_idea']['title']}: {state['selected_idea']['description']}"
    constraints_text = "\n".join([f"- {c}" for c in state["constraints"]])
    
    prompt = get_prompt("scenario_transformer").format(
        idea=idea_text,
        constraints=constraints_text,
        **state["employer_input"]
    )
    
    config = get_llm_config().get_config("scenario_transformer")
    logger.debug(f"Using LLM: {config['provider']}/{config['model']}")
    
    llm = get_llm(provider=config["provider"], model=config["model"], temperature=0.8)
    result = llm.invoke(prompt)
    
    logger.debug("Scenario transformed")
    return {"scenario": result.content}


def adversarial_agent(state: GraphState) -> dict:
    """Red-team the scenario to find vulnerabilities."""
    logger.debug("Node: adversarial_agent - Starting...")
    
    constraints_text = "\n".join([f"- {c}" for c in state["constraints"]])
    
    prompt = get_prompt("adversarial_agent").format(
        scenario=state["scenario"],
        constraints=constraints_text
    )
    
    config = get_llm_config().get_config("adversarial_agent")
    logger.debug(f"Using LLM: {config['provider']}/{config['model']}")
    
    llm = get_llm(provider=config["provider"], model=config["model"], temperature=0.9)
    structured_llm = llm.with_structured_output(Vulnerabilities)
    
    result = structured_llm.invoke(prompt)
    logger.debug(f"Found {len(result.vulnerabilities)} vulnerabilities")
    
    return {"vulnerabilities": [v.model_dump() for v in result.vulnerabilities]}


def patch_node(state: GraphState) -> dict:
    """Patch vulnerabilities in scenario and constraints."""
    logger.debug("Node: patch_node - Starting...")
    
    constraints_text = "\n".join([f"- {c}" for c in state["constraints"]])
    vulnerabilities_text = "\n".join([
        f"- {v['exploit_type']}: {v['description']}"
        for v in state["vulnerabilities"]
    ])
    
    prompt = get_prompt("patch_node").format(
        scenario=state["scenario"],
        constraints=constraints_text,
        vulnerabilities=vulnerabilities_text
    )
    
    config = get_llm_config().get_config("patch_node")
    logger.debug(f"Using LLM: {config['provider']}/{config['model']}")
    
    llm = get_llm(provider=config["provider"], model=config["model"], temperature=0.6)
    
    # Define a simple schema for patched output
    from pydantic import BaseModel
    class PatchedOutput(BaseModel):
        patched_scenario: str
        patched_constraints: list[str]
    
    structured_llm = llm.with_structured_output(PatchedOutput)
    result = structured_llm.invoke(prompt)
    
    logger.debug("Vulnerabilities patched")
    
    return {
        "scenario": result.patched_scenario,
        "constraints": result.patched_constraints
    }


def evaluation_designer(state: GraphState) -> dict:
    """Design scoring rubric for the assignment."""
    logger.debug("Node: evaluation_designer - Starting...")
    
    constraints_text = "\n".join([f"- {c}" for c in state["constraints"]])
    
    prompt = get_prompt("evaluation_designer").format(
        scenario=state["scenario"],
        constraints=constraints_text
    )
    
    config = get_llm_config().get_config("evaluation_designer")
    logger.debug(f"Using LLM: {config['provider']}/{config['model']}")
    
    llm = get_llm(provider=config["provider"], model=config["model"], temperature=0.5)
    structured_llm = llm.with_structured_output(EvaluationRubric)
    
    result = structured_llm.invoke(prompt)
    logger.debug("Evaluation rubric designed")
    
    return {"evaluation_rubric": result.model_dump()}


def prd_generator(state: GraphState) -> dict:
    """Assemble final PRD document with structured output."""
    logger.debug("Node: prd_generator - Starting...")
    
    try:
        from prd_inator.schema import FinalPRD
        
        constraints_text = "\n".join([f"- {c}" for c in state["constraints"]])
        rubric_text = str(state["evaluation_rubric"])
        vulnerabilities_text = "\n".join([
            f"- {v['exploit_type']}: {v['description']}"
            for v in state["vulnerabilities"]
        ])
        
        prompt = get_prompt("prd_generator").format(
            scenario=state["scenario"],
            constraints=constraints_text,
            rubric=rubric_text,
            vulnerabilities=vulnerabilities_text
        )
        
        config = get_llm_config().get_config("prd_generator")
        logger.debug(f"Using LLM: {config['provider']}/{config['model']}")
        
        llm = get_llm(provider=config["provider"], model=config["model"], temperature=0.4)
        structured_llm = llm.with_structured_output(FinalPRD)
        
        result = structured_llm.invoke(prompt)
        logger.debug("PRD generated successfully")
        
        return {
            "candidate_prd": result.candidate_prd,
            "evaluation_rubric_text": result.evaluation_rubric,
            "scoring_signals": result.scoring_signals
        }
    
    except Exception as e:
        logger.error(f"Error in prd_generator: {e}")
        raise
