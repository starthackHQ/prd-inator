"""Pipeline node implementations."""
from typing import Literal
from prd_inator.state import GraphState
from prd_inator.schema import (
    IdeaList, AntiAIScores, Constraints, Vulnerabilities
)
from prd_inator.utils import get_prompt, logger
from prd_inator.config import get_llm


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
        
        llm = get_llm("idea_divergence")
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
        
        llm = get_llm("diversity_enforcer")
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
        
        llm = get_llm("anti_ai_filter")
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
    
    llm = get_llm("constraint_injector")
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
    """Convert idea into structured scenario with all PRD components."""
    logger.debug("Node: scenario_transformer - Starting...")
    
    from prd_inator.schema import StructuredScenario
    
    idea_text = f"{state['selected_idea']['title']}: {state['selected_idea']['description']}"
    constraints_text = "\n".join([f"- {c}" for c in state["constraints"]])
    
    prompt = get_prompt("scenario_transformer").format(
        idea=idea_text,
        constraints=constraints_text,
        **state["employer_input"]
    )
    
    llm = get_llm("scenario_transformer")
    structured_llm = llm.with_structured_output(StructuredScenario)
    
    result = structured_llm.invoke(prompt)
    logger.debug("Structured scenario created")
    
    return {"scenario": result.model_dump()}


def adversarial_agent(state: GraphState) -> dict:
    """Red-team the scenario to find vulnerabilities."""
    logger.debug("Node: adversarial_agent - Starting...")
    
    constraints_text = "\n".join([f"- {c}" for c in state["constraints"]])
    
    prompt = get_prompt("adversarial_agent").format(
        scenario=state["scenario"],
        constraints=constraints_text
    )
    
    llm = get_llm("adversarial_agent")
    structured_llm = llm.with_structured_output(Vulnerabilities)
    
    result = structured_llm.invoke(prompt)
    logger.debug(f"Found {len(result.vulnerabilities)} vulnerabilities")
    
    return {"vulnerabilities": [v.model_dump() for v in result.vulnerabilities]}


def patch_node(state: GraphState) -> dict:
    """Patch vulnerabilities in structured scenario."""
    logger.debug("Node: patch_node - Starting...")
    
    from prd_inator.schema import StructuredScenario
    import json
    
    scenario_text = json.dumps(state["scenario"], indent=2)
    vulnerabilities_text = "\n".join([
        f"- {v['exploit_type']}: {v['description']}"
        for v in state["vulnerabilities"]
    ])
    
    prompt = get_prompt("patch_node").format(
        scenario=scenario_text,
        vulnerabilities=vulnerabilities_text
    )
    
    llm = get_llm("patch_node")
    structured_llm = llm.with_structured_output(StructuredScenario)
    
    result = structured_llm.invoke(prompt)
    logger.debug("Vulnerabilities patched")
    
    return {"scenario": result.model_dump()}


def prd_generator(state: GraphState) -> dict:
    """Assemble final PRD from structured scenario."""
    logger.debug("Node: prd_generator - Starting...")
    
    try:
        from prd_inator.schema import CandidatePRD
        import json
        
        scenario_text = json.dumps(state["scenario"], indent=2)
        tech_stack = state["employer_input"]["tech_stack"]
        
        prompt = get_prompt("prd_generator").format(
            scenario=scenario_text,
            tech_stack=tech_stack
        )
        
        llm = get_llm("prd_generator")
        structured_llm = llm.with_structured_output(CandidatePRD)
        
        result = structured_llm.invoke(prompt)
        logger.debug("PRD assembled successfully")
        
        # Format structured PRD into markdown
        prd = result
        candidate_prd_md = f"""# 1. Objective & Context

{prd.objective_context}

Subtle product value:
{chr(10).join(f'* {v}' for v in prd.product_value)}

---

# 2. Technical Stack

{chr(10).join(f'* {t}' for t in prd.tech_stack)}

---

# 3. Core Requirements

{chr(10).join(f'{i+1}. {req.summary}{chr(10)}{chr(10).join(f"   * {d}" for d in req.details)}' for i, req in enumerate(prd.core_requirements))}

---

# 4. Functional Requirements

{chr(10).join(f'## {comp.component_name}{chr(10)}{chr(10)}### `{comp.interface}`{chr(10)}{chr(10)}{chr(10).join(f"* {d}" for d in comp.details)}' for comp in prd.functional_requirements)}

---

# 5. Non-Functional Requirements

## Performance
{chr(10).join(f'* {r}' for r in prd.non_functional_requirements.performance)}

## Resilience
{chr(10).join(f'* {r}' for r in prd.non_functional_requirements.resilience)}

## Security
{chr(10).join(f'* {r}' for r in prd.non_functional_requirements.security)}

## Developer Experience
{chr(10).join(f'* {r}' for r in prd.non_functional_requirements.developer_experience)}

---

# 6. User Flow

{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(prd.user_flow))}
"""
        
        return {"candidate_prd": candidate_prd_md}
    
    except Exception as e:
        logger.error(f"Error in prd_generator: {e}")
        raise
