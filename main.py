"""CLI entry point for prd-inator."""
import os
from prd_inator import generate_prd
from dotenv import load_dotenv

load_dotenv()


def main():
    """Run the PRD generation pipeline."""
    
    # Check if langchain-openai is installed
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        print("❌ Error: langchain-openai is required for the CLI")
        print("Install it with: pip install langchain-openai")
        print("\nOr use the library API with your own LLM provider.")
        return
    
    # Get employer inputs
    print("Enter assignment requirements:")
    role = input("Role (e.g., Backend Engineer, Full-stack Developer): ").strip()
    tech_stack = input("Tech Stack (e.g., Python/FastAPI, React/Node.js): ").strip()
    domain = input("Domain (e.g., fintech, e-commerce, healthcare): ").strip()
    seniority = input("Seniority (e.g., junior, mid-level, senior): ").strip()
    
    print("\nRunning pipeline...\n")
    
    try:
        # Initialize LLM
        llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL", "gpt-4o"),
            temperature=0.7
        )
        
        result = generate_prd(
            role=role,
            tech_stack=tech_stack,
            domain=domain,
            seniority=seniority,
            llm=llm
        )
        
        print("✅ Pipeline complete!\n")
        
        # Save outputs
        with open("candidate_prd.md", "w", encoding="utf-8") as f:
            f.write(result.candidate_prd)
        print("📄 Candidate PRD saved to candidate_prd.md")
        
        with open("evaluation_rubric.md", "w", encoding="utf-8") as f:
            f.write(result.evaluation_rubric)
        print("📄 Evaluation rubric saved to evaluation_rubric.md")
        
        with open("scoring_signals.md", "w", encoding="utf-8") as f:
            f.write(result.scoring_signals)
        print("📄 Scoring signals saved to scoring_signals.md")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
