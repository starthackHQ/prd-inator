"""
Example usage of prd-inator as a library.

Run this after installing: pip install prd-inator
"""

from prd_inator import generate_prd, LLMConfig


def basic_example():
    """Basic usage - simplest way to generate a PRD."""
    print("=" * 60)
    print("BASIC EXAMPLE")
    print("=" * 60)
    
    result = generate_prd(
        role="Backend Engineer",
        tech_stack="Python, FastAPI, PostgreSQL",
        domain="Enterprise Data Collaboration and Governance",
        seniority="Mid-level"
    )
    
    # Access the results
    print(f"Candidate PRD length: {len(result.candidate_prd)} chars")
    print(f"Evaluation rubric length: {len(result.evaluation_rubric)} chars")
    print(f"Scoring signals length: {len(result.scoring_signals)} chars")
    
    # Save to files
    with open("assignment.md", "w", encoding="utf-8") as f:
        f.write(result.candidate_prd)
    
    print("\n✅ PRD generated and saved to assignment.md")


def advanced_example():
    """Advanced usage - custom LLM configuration."""
    print("\n" + "=" * 60)
    print("ADVANCED EXAMPLE - Custom LLM Config")
    print("=" * 60)
    
    # Configure different models for different nodes
    config = LLMConfig(
        default_provider="openai",
        default_model="gpt-4o",
        node_configs={
            # Use cheaper model for simple tasks
            "diversity_enforcer": {"model": "gpt-4o-mini"},
            "anti_ai_filter": {"model": "gpt-4o-mini"},
            
            # Use Claude for adversarial thinking
            "adversarial_agent": {
                "provider": "gemini",
                "model": "gemini-3-flash-preview"
            }
        }
    )
    
    result = generate_prd(
        role="Frontend Developer",
        tech_stack="React, TypeScript, Next.js",
        domain="Healthcare",
        seniority="Senior",
        llm_config=config
    )
    
    print(f"\n✅ PRD generated with custom LLM config")
    print(f"Selected idea: {result.raw_state['selected_idea']['title']}")


def batch_example():
    """Generate multiple PRDs for different roles."""
    print("\n" + "=" * 60)
    print("BATCH EXAMPLE - Multiple PRDs")
    print("=" * 60)
    
    roles = [
        {
            "role": "Backend Engineer",
            "tech_stack": "Go, gRPC, PostgreSQL",
            "domain": "E-commerce",
            "seniority": "Junior"
        },
        {
            "role": "Full-stack Developer",
            "tech_stack": "React, Node.js, MongoDB",
            "domain": "SaaS",
            "seniority": "Mid-level"
        }
    ]
    
    for i, role_spec in enumerate(roles, 1):
        print(f"\nGenerating PRD {i}/{len(roles)}...")
        result = generate_prd(**role_spec)
        
        filename = f"prd_{i}_{role_spec['role'].replace(' ', '_').lower()}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result.candidate_prd)
        
        print(f"✅ Saved to {filename}")


if __name__ == "__main__":
    # Run examples
    basic_example()
    
    # Uncomment to run advanced examples:
    # advanced_example()
    # batch_example()
