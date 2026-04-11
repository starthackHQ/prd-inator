"""Pipeline node implementations."""
from typing import Literal
from prd_inator.state import GraphState
from prd_inator.schema import (
    IdeaList, AntiAIScores, Constraints, Vulnerabilities,
    EvaluationRubric, CritiqueResult
)
from prd_inator.utils.llm import get_llm
from prd_inator.utils.prompts import get_prompt
from prd_inator.config import get_llm_config
from langgraph.types import Command


def employer_input_node(state: GraphState) -> dict:
    """Validate employer inputs."""
    print("🔄 Node: employer_input - Starting...")
    required_fields = ["role", "tech_stack", "domain", "seniority"]
    employer_input = state.get("employer_input", {})
    
    for field in required_fields:
        if not employer_input.get(field):
            raise ValueError(f"Missing required field: {field}")
    
    print("✅ Employer input validated")
    return {
        "idea_loop_count": 0,
        "critique_iterations": 0
    }


def idea_divergence_engine(state: GraphState) -> dict:
    """Generate 15 diverse project ideas."""
    print("🔄 Node: idea_divergence_engine - Starting...")
    
    try:
        prompt = get_prompt("idea_divergence").format(**state["employer_input"])
        
        print(f"📝 Prompt length: {len(prompt)} chars")
        config = get_llm_config().get_config("idea_divergence")
        print(f"🤖 Using LLM: {config['provider']}/{config['model']}")
        
        llm = get_llm(provider=config["provider"], model=config["model"], temperature=0.9)
        structured_llm = llm.with_structured_output(IdeaList)
        
        print("📡 Calling LLM...")
        result = structured_llm.invoke(prompt)
        print(f"✅ Got {len(result.ideas)} ideas")
        
        return {"ideas": [idea.model_dump() for idea in result.ideas]}
    
    except Exception as e:
        print(f"❌ Error in idea_divergence_engine: {e}")
        raise  # Let RetryPolicy handle transient errors


def diversity_enforcer(state: GraphState) -> dict:
    """Remove semantic duplicates from ideas."""
    try:
        ideas_text = "\n\n".join([
            f"{i+1}. {idea['title']}: {idea['description']}"
            for i, idea in enumerate(state["ideas"])
        ])
        
        prompt = get_prompt("diversity_enforcer").format(ideas=ideas_text)
        
        config = get_llm_config().get_config("diversity_enforcer")
        llm = get_llm(provider=config["provider"], model=config["model"], temperature=0.3)
        structured_llm = llm.with_structured_output(IdeaList)
        
        result = structured_llm.invoke(prompt)
        return {"filtered_ideas": [idea.model_dump() for idea in result.ideas]}
    
    except Exception as e:
        print(f"❌ Error in diversity_enforcer: {e}")
        raise


def anti_ai_filter(state: GraphState) -> dict:
    """Score ideas on AI-resistance and select the best."""
    try:
        ideas_text = "\n\n".join([
            f"{i+1}. {idea['title']}: {idea['description']}"
            for i, idea in enumerate(state["filtered_ideas"])
        ])
        
        prompt = get_prompt("anti_ai_filter").format(ideas=ideas_text)
        
        config = get_llm_config().get_config("anti_ai_filter")
        llm = get_llm(provider=config["provider"], model=config["model"], temperature=0.2)
        structured_llm = llm.with_structured_output(AntiAIScores)
        
        result = structured_llm.invoke(prompt)
        scores = result.scores
        
        # Filter ideas with total_score <= 5 (lower is better)
        passing_ideas = [s for s in scores if s.total_score <= 5]
        
        if len(passing_ideas) < 2:
            # Not enough good ideas, will loop back
            return {"selected_idea": {}}
        
        # Select the best (lowest score)
        best = min(passing_ideas, key=lambda x: x.total_score)
        
        # Find the original idea
        for idea in state["filtered_ideas"]:
            if idea["title"] == best.idea_title:
                return {"selected_idea": idea}
        
        return {"selected_idea": {}}
    
    except Exception as e:
        print(f"❌ Error in anti_ai_filter: {e}")
        raise


def should_regenerate_ideas(state: GraphState) -> Literal["regenerate", "continue"]:
    """Conditional edge: check if we need to regenerate ideas."""
    if not state.get("selected_idea"):
        if state["idea_loop_count"] < 3:
            return "regenerate"
        else:
            raise RuntimeError("Failed to generate suitable ideas after 3 attempts")
    return "continue"


def constraint_injector(state: GraphState) -> dict:
    """Inject deliberate friction into the selected idea."""
    idea_text = f"{state['selected_idea']['title']}: {state['selected_idea']['description']}"
    seniority = state["employer_input"].get("seniority", "mid-level")
    
    prompt = get_prompt("constraint_injector").format(idea=idea_text, seniority=seniority)
    
    config = get_llm_config().get_config("constraint_injector")
    llm = get_llm(provider=config["provider"], model=config["model"], temperature=0.7)
    structured_llm = llm.with_structured_output(Constraints)
    
    result = structured_llm.invoke(prompt)
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
    idea_text = f"{state['selected_idea']['title']}: {state['selected_idea']['description']}"
    constraints_text = "\n".join([f"- {c}" for c in state["constraints"]])
    seniority = state["employer_input"].get("seniority", "mid-level")
    
    prompt = get_prompt("scenario_transformer").format(
        idea=idea_text,
        constraints=constraints_text,
        seniority=seniority
    )
    
    config = get_llm_config().get_config("scenario_transformer")
    llm = get_llm(provider=config["provider"], model=config["model"], temperature=0.8)
    result = llm.invoke(prompt)
    
    return {"scenario": result.content}


def adversarial_agent(state: GraphState) -> dict:
    """Red-team the scenario to find vulnerabilities."""
    constraints_text = "\n".join([f"- {c}" for c in state["constraints"]])
    
    prompt = get_prompt("adversarial_agent").format(
        scenario=state["scenario"],
        constraints=constraints_text
    )
    
    config = get_llm_config().get_config("adversarial_agent")
    llm = get_llm(provider=config["provider"], model=config["model"], temperature=0.9)
    structured_llm = llm.with_structured_output(Vulnerabilities)
    
    result = structured_llm.invoke(prompt)
    return {"vulnerabilities": [v.model_dump() for v in result.vulnerabilities]}


def patch_node(state: GraphState) -> dict:
    """Patch vulnerabilities in scenario and constraints."""
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
    llm = get_llm(provider=config["provider"], model=config["model"], temperature=0.6)
    
    # Define a simple schema for patched output
    from pydantic import BaseModel
    class PatchedOutput(BaseModel):
        patched_scenario: str
        patched_constraints: list[str]
    
    structured_llm = llm.with_structured_output(PatchedOutput)
    result = structured_llm.invoke(prompt)
    
    return {
        "scenario": result.patched_scenario,
        "constraints": result.patched_constraints
    }


def evaluation_designer(state: GraphState) -> dict:
    """Design scoring rubric for the assignment."""
    constraints_text = "\n".join([f"- {c}" for c in state["constraints"]])
    
    prompt = get_prompt("evaluation_designer").format(
        scenario=state["scenario"],
        constraints=constraints_text
    )
    
    config = get_llm_config().get_config("evaluation_designer")
    llm = get_llm(provider=config["provider"], model=config["model"], temperature=0.5)
    structured_llm = llm.with_structured_output(EvaluationRubric)
    
    result = structured_llm.invoke(prompt)
    return {"evaluation_rubric": result.model_dump()}


def self_critique_loop(state: GraphState) -> Command[Literal["constraint_injector", "prd_generator"]]:
    """Meta-critique the assignment quality with Command for routing."""
    constraints_text = "\n".join([f"- {c}" for c in state["constraints"]])
    rubric_text = str(state["evaluation_rubric"])
    seniority = state["employer_input"].get("seniority", "mid-level")
    
    prompt = get_prompt("self_critique").format(
        scenario=state["scenario"],
        constraints=constraints_text,
        rubric=rubric_text,
        seniority=seniority
    )
    
    config = get_llm_config().get_config("self_critique")
    llm = get_llm(provider=config["provider"], model=config["model"], temperature=0.3)
    structured_llm = llm.with_structured_output(CritiqueResult)
    
    result = structured_llm.invoke(prompt)
    
    # Use Command to update state AND route
    if not result.passed and state["critique_iterations"] < 3:
        return Command(
            update={"critique_iterations": state["critique_iterations"] + 1},
            goto="constraint_injector"
        )
    
    return Command(goto="prd_generator")


def prd_generator(state: GraphState) -> dict:
    """Assemble final PRD document."""
    try:
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
        llm = get_llm(provider=config["provider"], model=config["model"], temperature=0.4)
        result = llm.invoke(prompt)
        
        return {"final_prd": result.content}
    
    except Exception as e:
        print(f"❌ Error in prd_generator: {e}")
        raise

