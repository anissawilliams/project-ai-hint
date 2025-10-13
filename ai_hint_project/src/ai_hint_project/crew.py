from crewai import Crew, Agent, Task
import yaml
import os
import re
from datetime import datetime

from crewai import TaskOutput

# ✅ Use LiteLLM via CrewAI's built-in support
from litellm import completion

class LiteLLMWrapper:
    def __init__(self, model: str, api_base: str):
        self.model = model
        self.api_base = api_base

    def __call__(self, prompt: str) -> str:
        response = completion(
            model=self.model,
            api_base=self.api_base,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]

# ✅ Instantiate the wrapper for Ollama
llm = LiteLLMWrapper(model="ollama/llama3", api_base="http://localhost:11434")

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def create_crew(user_query):
    print("✅ create_crew() called")

    base_dir = os.path.dirname(__file__)
    agents_config = load_yaml(os.path.join(base_dir, 'config/agents.yaml'))
    tasks_config = load_yaml(os.path.join(base_dir, 'config/tasks.yaml'))

    # Phase 1: Query Optimizer
    optimizer = Agent(
        role=agents_config['query_optimizer']['role'],
        goal=agents_config['query_optimizer']['goal'],
        backstory=agents_config['query_optimizer']['backstory'],
        llm=llm
    )

    optimize_task = Task(
        name="Optimize Query",
        description="Improve the user's question: {user_query}".format(user_query=user_query),
        expected_output="A clearer, more specific version of the question",
        agent=optimizer
    )

    crew_opt = Crew(
        agents=[optimizer],
        tasks=[optimize_task],
        verbose=True
    )




    print("🧠 Running Query Optimizer...")
    result_opt = crew_opt.kickoff()
    #optimized_query = result_opt.tasks_output[0].model_validate_json().final_answer

    

    try:
        parsed = TaskOutput.model_validate_json(result_opt.tasks_output[0].raw)
        final_answer = parsed.final_answer
    except Exception:
        print("⚠️ JSON parsing failed. Falling back to regex.")
        match = re.search(r"Final Answer:\s*(.*)", result_opt.tasks_output[0].raw, re.DOTALL)
        final_answer = match.group(1).strip() if match else result_opt.tasks_output[0].raw.strip()

        optimized_query = final_answer
    

    # Phase 2: Explainer
    explainer = Agent(
        role=agents_config['explainer']['role'],
        goal=agents_config['explainer']['goal'],
        backstory=agents_config['explainer']['backstory'],
        llm=llm
    )

    explain_task = Task(
        name="Explain Concept",
        description="Explain the topic: {optimized_query}".format(optimized_query=optimized_query),
        expected_output="A clear explanation with examples",
        agent=explainer
    )

    crew_explain = Crew(
        agents=[explainer],
        tasks=[explain_task],
        verbose=True
    )

    print("🧠 Running Explainer...")
    result_explain = crew_explain.kickoff()
    try:
        parsed = TaskOutput.model_validate_json(result_explain.tasks_output[0].raw)
        final_answer = parsed.final_answer
    except Exception:
        print("⚠️ JSON parsing failed. Falling back to regex.")
        match = re.search(r"Final Answer:\s*(.*)", result_explain.tasks_output[0].raw, re.DOTALL)
        final_answer = match.group(1).strip() if match else result_explain.tasks_output[0].raw.strip()

        explanation = final_answer

    


    return {
        "optimized_query": optimized_query,
        "explanation": explanation
    }
