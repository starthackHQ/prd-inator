"""LangGraph pipeline orchestration."""
from typing import Optional
from langgraph.graph import StateGraph, START, END
from prd_inator.state import GraphState
from prd_inator.config import LLMConfig, set_llm_config
from prd_inator.node import (
    employer_input_node,
    idea_divergence_engine,
    diversity_enforcer,
    anti_ai_filter,
    should_regenerate_ideas,
    constraint_injector,
    scenario_transformer,
    adversarial_agent,
    patch_node,
    evaluation_designer,
    self_critique_loop,
    prd_generator
)


def build_graph():
    """Build and compile the LangGraph pipeline."""
    
    # Initialize graph
    workflow = StateGraph(GraphState)
    
    # Add all nodes
    workflow.add_node("employer_input", employer_input_node)
    workflow.add_node("idea_divergence", idea_divergence_engine)
    workflow.add_node("diversity_enforcer", diversity_enforcer)
    workflow.add_node("anti_ai_filter", anti_ai_filter)
    workflow.add_node("constraint_injector", constraint_injector)
    workflow.add_node("scenario_transformer", scenario_transformer)
    workflow.add_node("adversarial_agent", adversarial_agent)
    workflow.add_node("patch_node", patch_node)
    workflow.add_node("evaluation_designer", evaluation_designer)
    workflow.add_node("self_critique", self_critique_loop, ends=["constraint_injector", "prd_generator"])
    workflow.add_node("prd_generator", prd_generator)
    
    # Use START node (not set_entry_point)
    workflow.add_edge(START, "employer_input")
    
    # Linear flow: employer_input -> idea_divergence
    workflow.add_edge("employer_input", "idea_divergence")
    workflow.add_edge("idea_divergence", "diversity_enforcer")
    workflow.add_edge("diversity_enforcer", "anti_ai_filter")
    
    # Conditional edge: Loop 1 (anti_ai_filter -> idea_divergence or continue)
    workflow.add_conditional_edges(
        "anti_ai_filter",
        should_regenerate_ideas,
        {
            "regenerate": "idea_divergence",
            "continue": "constraint_injector"
        }
    )
    
    # Linear flow through constraint injection and scenario building
    workflow.add_edge("constraint_injector", "scenario_transformer")
    workflow.add_edge("scenario_transformer", "adversarial_agent")
    workflow.add_edge("adversarial_agent", "patch_node")
    workflow.add_edge("patch_node", "evaluation_designer")
    workflow.add_edge("evaluation_designer", "self_critique")
    
    # self_critique uses Command, no conditional edge needed
    # Command will route to either constraint_injector or prd_generator
    
    # Final edge to END
    workflow.add_edge("prd_generator", END)
    
    # Compile and return
    return workflow.compile()


def run_pipeline(
    employer_input: dict,
    llm_config: Optional[LLMConfig] = None
) -> dict:
    """
    Run the complete pipeline with employer inputs.
    
    Args:
        employer_input: Dict with role, tech_stack, domain, seniority
        llm_config: Optional LLMConfig to override default configuration
        
    Returns:
        Final state dict with generated PRD
    """
    # Set LLM config if provided
    if llm_config:
        set_llm_config(llm_config)
    
    graph = build_graph()
    
    initial_state = {
        "employer_input": employer_input,
        "ideas": [],
        "filtered_ideas": [],
        "selected_idea": {},
        "idea_loop_count": 0,
        "constraints": [],
        "scenario": "",
        "vulnerabilities": [],
        "evaluation_rubric": {},
        "critique_iterations": 0,
        "final_prd": ""
    }
    
    result = graph.invoke(initial_state)
    return result

