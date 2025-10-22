import os
import yaml
import re
from crewai import Crew, Agent, Task
from langchain_community.chat_models import ChatOllama


from sentence_transformers import SentenceTransformer
import faiss
import json
from . import levels

import os
from langchain_groq import ChatGroq

llm = ChatGroq(
    model_name="mixtral-8x7b-32768",  # or "llama3-8b-8192"
    temperature=0.7,
    groq_api_key=os.getenv("GROQ_API_KEY")
)


from .tools.rag_tool import build_rag_tool

base_dir = os.path.dirname(os.path.abspath(__file__))
rag_folder = os.path.join(base_dir, "baeldung_scraper")

rag_tool = build_rag_tool(
    index_path=os.path.join(rag_folder, "baeldung_index.faiss"),
    chunks_path=os.path.join(rag_folder, "chunks.json")
)


def load_rag_store(folder="baeldung_scraper"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    rag_path = os.path.join(base_dir, folder)

    index_path = os.path.join(rag_path, "baeldung_index.faiss")
    chunks_path = os.path.join(rag_path, "chunks.json")

    if not os.path.exists(index_path):
        raise FileNotFoundError(f"FAISS index not found at: {index_path}")
    if not os.path.exists(chunks_path):
        raise FileNotFoundError(f"Chunks file not found at: {chunks_path}")

    index = faiss.read_index(index_path)
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    return index, chunks




# Load YAML config
def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

# Detect if input contains code


def is_code_input(text):
    # Look for actual code patterns, not just symbols
    code_patterns = [
        r"\bdef\b", r"\bclass\b", r"\bimport\b", r"\breturn\b",
        r"\bif\b\s*\(?.*?\)?\s*:", r"\bfor\b\s*\(?.*?\)?\s*:", r"\bwhile\b\s*\(?.*?\)?\s*:",
        r"\btry\b\s*:", r"\bexcept\b\s*:", r"\w+\s*=\s*.+", r"\w+\(.*?\)", r"{.*?}", r"<.*?>"
    ]
    return any(re.search(pattern, text) for pattern in code_patterns)

# Persona-specific reactions to pasted code
persona_reactions = {
    "Batman": "Code received. Looks like a breach in logic. Let’s patch the vulnerability before it spreads.",
    "Yoda": "Code, you have pasted. Analyze it, we must. Hidden, the bug may be.",
    "Spider-Gwen": "Nice drop! Let’s swing through this syntax and catch any bugs midair.",
    "Shuri": "Vibranium-grade logic? Let’s scan it with Wakandan tech and optimize the flow.",
    "Elsa": "This code is… chaotic. Let me freeze the bugs and refactor with elegance.",
    "Wednesday Addams": "You’ve pasted code. How delightfully broken it looks. Let’s dissect it like a corpse.",
    "Iron Man": "Code drop detected. Let’s run diagnostics and upgrade it to Stark-level performance.",
    "Nova": "Cosmic code detected. Let’s orbit through its logic and illuminate the stars within.",
    "Zee": "Code incoming! Let’s treat this like a boss fight and break it down tactically.",
    "Sherlock Holmes": "Ah, a code snippet. Let’s deduce its structure and uncover any hidden flaws."
}

def create_crew(persona: str, user_question: str):
    print("✅ create_crew() called with persona:", persona)

    base_dir = os.path.dirname(__file__)
    agents_config = load_yaml(os.path.join(base_dir, 'config/agents.yaml'))
    tasks_config = load_yaml(os.path.join(base_dir, 'config/tasks.yaml'))

    agent_cfg = agents_config['agents'].get(persona)
    if not agent_cfg:
        raise ValueError(f"Unknown persona: {persona}")

    agent = Agent(
        role=agent_cfg['role'],
        goal=agent_cfg['goal'],
        backstory=agent_cfg['backstory'],
        level=agent_cfg.get('level', 'beginner'),
        verbose=False,
        llm=llm
    )

    reaction = persona_reactions.get(persona, "")
    task_description = f"{reaction}\n\n{user_question}" if is_code_input(user_question) else user_question

    # 🔍 Use RAG tool to retrieve context
    context = rag_tool(user_question)


    task_template = tasks_config['tasks']['explainer']
    task = Task(
        name=task_template['name'],
        description=task_template['description'].format(query=f"{task_description}\n\nRelevant Java context:\n{context}"),
        expected_output=task_template['expected_output'],
        agent=agent
    )

    crew = Crew(agents=[agent], tasks=[task], verbose=True)
    result = crew.kickoff()
    levels.update_level(persona)

    cleaned_content = re.sub(r"<think>.*?</think>\n?", "", result.tasks_output[0].raw, flags=re.DOTALL)
    return cleaned_content
