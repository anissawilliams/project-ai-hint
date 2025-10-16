import sys
sys.path.insert(0, "/Users/anissawilliams/research/project-ai-hint/crewAI")  # adjust to your actual path

from crewai import Crew, Agent, Task, TaskOutput
import yaml
import os
import re
from datetime import datetime

from pydantic import BaseModel, ValidationError
os.environ["LITELLM_PROVIDER"] = "ollama"



MODEL_ROUTING = {
    "optimizer": "deepseek-coder",
    "debugger": "deepseek-coder",
    "explainer": "deepseek-r1:7b",
    "theorist": "deepseek-r1:7b",
    "guide": "deepseek-r1:7b",
    "beginner_query_optimizer": "deepseek-r1:7b",
    "advanced_query_optimizer": "deepseek-r1:7b",
}

from langchain.llms import Ollama

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def create_crew(user_query, user_level, user_code=None, depth="Thorough"):
    print("✅ create_crew() called")

    base_dir = os.path.dirname(__file__)
    agents_config = load_yaml(os.path.join(base_dir, 'config/agents.yaml'))

    def select_model(agent_key: str, depth: str = "Thorough") -> str:
        if agent_key in ["explainer", "guide", "theorist"]:
            return "deepseek-coder" if depth == "Fast" else "deepseek-r1:7b"
        return MODEL_ROUTING.get(agent_key, "deepseek-coder")  # fallback default

    def run_agent(agent_key, task_name, description, expected_output):
        agent_cfg = agents_config[agent_key]
        # Choose model based on agent_key and depth mode (fast or thorough)
       
        agent_cfg = agents_config[agent_key]
        model_name = "ollama/" + select_model(agent_key, depth)
        llm = Ollama(model=model_name)
    
        agent = Agent(
            role=agent_cfg['role'],
            goal=agent_cfg['goal'],
            backstory=agent_cfg['backstory'],
            level=agent_cfg['level'],
            verbose=True,
            llm=llm
        )
        task = Task(
            name=task_name,
            description=description,
            expected_output=expected_output,
            agent=agent
        )
        crew = Crew(agents=[agent], tasks=[task], verbose=True)
        print(f"🧠 Running {agent_key}...")
        print(f"🧠 Using model {model_name} for agent {agent_key}")
        print(f"🧠 Prompt for {agent_key}:\n{description}")
        result = crew.kickoff()

        #match = re.search(r"Final Answer:\s*(.*)", result.tasks_output[0].raw, re.DOTALL)
       
        cleaned_content = re.sub(r"<think>.*?</think>\n?", "",result.tasks_output[0].raw, flags=re.DOTALL) 
        return cleaned_content

    explanation = None
    optimization = None
    debugging = None
    theory = None
    guide = None

    # Phase 1: Optimize query

    optimized_query = run_agent(
            f"{user_level}_query_optimizer",
            "Optimize Query",
            f"Improve the user's question: {user_query}",
            "optimized_query"
        )
    explanation = run_agent(
            f"{user_level}_explainer",
            "Explain Concept",
            f"Explain the topic: {optimized_query}",
            "explanation"
        )
    guide = run_agent(
            "guide",
            "Step-by-Step Guide",
            f"Guide the user through: {optimized_query}",
            "guide"
    ) if user_level == "beginner" else None

    optimization = run_agent(
            "optimizer",
            "Optimize Code",
            f"Refactor this code for clarity and performance: {user_code}",
            "optimization"
        ) if user_code else None


    theory = run_agent(
            "theorist",
            "Explore Theory",
            f"Explore the principles behind: {optimized_query}",
            "theory"
    ) if user_level == "advanced" else None

   #level-agnostic
    debugging = run_agent(
        "debugger",
        "Debug Code",
        f"Analyze and improve this code: {user_code}",
        "debugging"
    ) if user_code else None


    return {
        "optimized_query": optimized_query,
        "explanation": explanation,
        "guide": guide,
        "debugging": debugging,
        "optimization": optimization,
        "theory": theory
    }

