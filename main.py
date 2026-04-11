"""CLI entry point for prd-inator."""
from prd_inator import generate_prd
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
    
    print("\n⚙️  Running pipeline...\n")
    
    try:
        # Use the simple API
        result = generate_prd(
            role=role,
            tech_stack=tech_stack,
            domain=domain,
            seniority=seniority
        )
        
        print("✅ Pipeline complete!\n")
        
        # Save candidate PRD
        print("=" * 80)
        print("CANDIDATE-FACING PRD")
        print("=" * 80)
        print(result.candidate_prd)
        print("\n")
        
        with open("candidate_prd.md", "w", encoding="utf-8") as f:
            f.write(result.candidate_prd)
        print("📄 Candidate PRD saved to candidate_prd.md\n")
        
        # Save evaluation rubric
        with open("evaluation_rubric.md", "w", encoding="utf-8") as f:
            f.write(result.evaluation_rubric)
        print("📄 Evaluation rubric saved to evaluation_rubric.md")
        
        # Save scoring signals
        with open("scoring_signals.md", "w", encoding="utf-8") as f:
            f.write(result.scoring_signals)
        print("📄 Scoring signals saved to scoring_signals.md")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
