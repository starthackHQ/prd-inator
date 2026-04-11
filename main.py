"""CLI entry point for prd-inator."""
from prd_inator import run_pipeline, LLMConfig
from dotenv import load_dotenv

load_dotenv()


def main():
    """Run the PRD generation pipeline."""
    print("🚀 PRD-inator: AI-Resistant Assignment Generator\n")
    
    # Get employer inputs
    print("Enter assignment requirements:")
    role = input("Role (e.g., Backend Engineer, Full-stack Developer): ").strip()
    tech_stack = input("Tech Stack (e.g., Python/FastAPI, React/Node.js): ").strip()
    domain = input("Domain (e.g., fintech, e-commerce, healthcare): ").strip()
    seniority = input("Seniority (e.g., junior, mid-level, senior): ").strip()
    
    employer_input = {
        "role": role,
        "tech_stack": tech_stack,
        "domain": domain,
        "seniority": seniority
    }
    
    # Optional: Configure LLMs
    # By default, reads from env vars: LLM_PROVIDER and LLM_MODEL
    # You can also override per-node or set defaults programmatically:
    
    # Example 1: Use same model for all nodes
    # llm_config = LLMConfig(default_provider="openai", default_model="gpt-4o")
    
    # Example 2: Use different models per node
    # llm_config = LLMConfig(
    #     default_provider="openai",
    #     default_model="gpt-4o",
    #     node_configs={
    #         "idea_divergence": {"model": "gpt-4o"},
    #         "anti_ai_filter": {"model": "gpt-4o-mini"},
    #         "adversarial_agent": {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"}
    #     }
    # )
    
    # Example 3: Let it read from environment variables (default behavior)
    llm_config = None  # Will use env vars: LLM_PROVIDER, LLM_MODEL, or per-node vars
    
    print("\n⚙️  Running pipeline...\n")
    
    try:
        result = run_pipeline(employer_input, llm_config=llm_config)
        
        print("✅ Pipeline complete!\n")
        print("=" * 80)
        print(result["final_prd"])
        print("=" * 80)
        
        # Optionally save to file
        with open("output_prd.md", "w") as f:
            f.write(result["final_prd"])
        print("\n📄 PRD saved to output_prd.md")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
