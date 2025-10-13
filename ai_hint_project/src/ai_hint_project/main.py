from datetime import datetime
from ai_hint_project.src.ai_hint_project import crew
from crew import create_crew  # Adjust path if needed

def run():
    """
    Run the programming tutor crew with sample inputs.
    """
    topic = "recursive functions"
    user_query = "Why does my recursive factorial function crash with a maximum recursion depth error?"

try:
    result = crew.kickoff()
    print("Crew result:", result)
except Exception as e:
    print("Error running crew:", e)


if __name__ == "__main__":
    run()
