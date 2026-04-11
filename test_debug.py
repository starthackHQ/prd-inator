"""Test script to debug pipeline."""
from prd_inator.graph import build_graph
from dotenv import load_dotenv

load_dotenv()

employer_input = {
    'role': 'Test',
    'tech_stack': 'Test',
    'domain': 'Test',
    'seniority': 'Test'
}

print('Building graph...')
graph = build_graph()
print('Graph built successfully')

initial_state = {
    'employer_input': employer_input,
    'ideas': [],
    'filtered_ideas': [],
    'selected_idea': {},
    'idea_loop_count': 0,
    'constraints': [],
    'scenario': '',
    'vulnerabilities': [],
    'evaluation_rubric': {},
    'critique_iterations': 0,
    'final_prd': ''
}

print('Starting pipeline...')
print('Calling employer_input node...')
try:
    result = graph.invoke(initial_state)
    print('Pipeline completed!')
    print(f"Final PRD length: {len(result.get('final_prd', ''))}")
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
