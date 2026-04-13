"""Example usage of prd-inator with the new simplified API."""

from langchain_openai import ChatOpenAI
from prd_inator import generate_prd

# Example 1: Simple usage with a single LLM for all nodes
def simple_example():
    """Use the same LLM for all pipeline nodes."""
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    
    result = generate_prd(
        role="Backend Engineer",
        tech_stack="Python, FastAPI, PostgreSQL",
        domain="Fintech",
        seniority="Mid-level",
        llm=llm
    )
    
    print("=== Candidate PRD ===")
    print(result.candidate_prd[:500])  # First 500 chars
    print("\n=== Evaluation Rubric ===")
    print(result.evaluation_rubric[:500])
    print("\n=== Scoring Signals ===")
    print(result.scoring_signals[:500])


# Example 2: Advanced usage with different LLMs per node
def advanced_example():
    """Use different LLMs for specific nodes."""
    from langchain_anthropic import ChatAnthropic
    
    # Default LLM for most nodes
    default_llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    
    # Use Claude for adversarial thinking
    adversarial_llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.9
    )
    
    # Use cheaper model for diversity enforcement
    cheap_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    result = generate_prd(
        role="Frontend Developer",
        tech_stack="React, TypeScript, Next.js",
        domain="Healthcare",
        seniority="Senior",
        llm=default_llm,
        node_llms={
            "adversarial_agent": adversarial_llm,
            "diversity_enforcer": cheap_llm
        }
    )
    
    # Save outputs
    with open("assignment.md", "w") as f:
        f.write(result.candidate_prd)
    
    with open("rubric.md", "w") as f:
        f.write(result.evaluation_rubric)
    
    with open("signals.md", "w") as f:
        f.write(result.scoring_signals)
    
    print("✅ PRD generated and saved to files!")


# Example 3: Using custom LLM configuration
def custom_llm_example():
    """Use your own custom LLM setup."""
    
    # You can use any LangChain-compatible LLM
    # This could be a local model, custom wrapper, etc.
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        max_tokens=4000,
        timeout=60,
        max_retries=3
    )
    
    result = generate_prd(
        role="DevOps Engineer",
        tech_stack="Kubernetes, Terraform, AWS",
        domain="Cloud Infrastructure",
        seniority="Senior",
        llm=llm
    )
    
    return result


if __name__ == "__main__":
    # Run simple example
    simple_example()
    
    # Uncomment to run advanced example
    # advanced_example()
    
    # Uncomment to run custom example
    # custom_llm_example()
