"""LangGraph pipeline orchestration."""
from typing import Dict
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy
from prd_inator.state import GraphState
from prd_inator.config import set_llms
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
    prd_generator
)


def build_graph():
    """Build and compile the LangGraph pipeline."""
    
    # Retry policy for LLM nodes (network failures, rate limits)
    llm_retry = RetryPolicy(max_attempts=3, initial_interval=1.0)
    
    # Initialize graph
    workflow = StateGraph(GraphState)
    
    # Add nodes with retry policies for LLM calls
    workflow.add_node("employer_input", employer_input_node)
    workflow.add_node("idea_divergence", idea_divergence_engine, retry_policy=llm_retry)
    workflow.add_node("diversity_enforcer", diversity_enforcer, retry_policy=llm_retry)
    workflow.add_node("anti_ai_filter", anti_ai_filter, retry_policy=llm_retry)
    workflow.add_node("constraint_injector", constraint_injector, retry_policy=llm_retry)
    workflow.add_node("scenario_transformer", scenario_transformer, retry_policy=llm_retry)
    workflow.add_node("adversarial_agent", adversarial_agent, retry_policy=llm_retry)
    workflow.add_node("patch_node", patch_node, retry_policy=llm_retry)
    workflow.add_node("prd_generator", prd_generator, retry_policy=llm_retry)
    
    workflow.add_edge(START, "employer_input")
    workflow.add_edge("employer_input", "idea_divergence")
    workflow.add_edge("idea_divergence", "diversity_enforcer")
    workflow.add_edge("diversity_enforcer", "anti_ai_filter")
    
    workflow.add_conditional_edges(
        "anti_ai_filter",
        should_regenerate_ideas,
        {
            "regenerate": "idea_divergence",
            "continue": "constraint_injector"
        }
    )
    
    workflow.add_edge("constraint_injector", "scenario_transformer")
    workflow.add_edge("scenario_transformer", "adversarial_agent")
    workflow.add_edge("adversarial_agent", "patch_node")
    workflow.add_edge("patch_node", "prd_generator")
    workflow.add_edge("prd_generator", END)
    
    return workflow.compile()


def run_pipeline(
    employer_input: dict,
    llm: BaseChatModel | Runnable | None = None,
    node_llms: Dict[str, BaseChatModel | Runnable] | None = None
) -> dict:
    """
    Run the complete pipeline with employer inputs.
    
    Args:
        employer_input: Dict with role, tech_stack, domain, seniority
        llm: Single LLM instance to use for all nodes
        node_llms: Per-node LLM overrides
        
    Returns:
        Final state dict with generated PRD
    """
    set_llms(default_llm=llm, node_llms=node_llms)
    
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
        "candidate_prd": ""
    }
    
    result = graph.invoke(initial_state)
    return result
