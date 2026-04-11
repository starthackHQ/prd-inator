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
        
        # Save candidate PRD
        print("=" * 80)
        print("CANDIDATE-FACING PRD")
        print("=" * 80)
        print(result["candidate_prd"])
        print("\n")
        
        with open("candidate_prd.md", "w", encoding="utf-8") as f:
            f.write(result["candidate_prd"])
        print("📄 Candidate PRD saved to candidate_prd.md\n")
        
        # Save evaluation rubric
        with open("evaluation_rubric.md", "w", encoding="utf-8") as f:
            f.write(result["evaluation_rubric_text"])
        print("📄 Evaluation rubric saved to evaluation_rubric.md")
        
        # Save scoring signals
        with open("scoring_signals.md", "w", encoding="utf-8") as f:
            f.write(result["scoring_signals"])
        print("📄 Scoring signals saved to scoring_signals.md")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
