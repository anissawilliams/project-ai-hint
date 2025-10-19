import langchain
import langchain_ollama
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from datetime import date
from langchain.globals import set_debug
import os
from getpass import getpass

set_debug(True)
#From https://colab.research.google.com/drive/1MsQNc7AMS3qY4Y94_ZN8ppWcNh0RgD-v?usp=sharing#scrollTo=HGz1kWy88tdO


llm = ChatOllama(
    model="llama3.1",
    temperature=0,
    api_key=CODE_LLAMAKEY,
    verbose=True,
    max_tokens=1024,
    # other params...
)
messages = [
    (
        "system",
        "You are a world class programming assistant that helps people find bugs in their code and fix them.",
    ),
    ("human", "Please help me explain how to use langchain with ollama."),
]
ai_msg = llm.invoke(messages)
#print(ai_msg)
#langchain.llm_cache = langchain_ollama.OllamaCache()


ai_msg_prompt = ChatPromptTemplate.from_messages([
   ("system", "You are a world class comedian."),
   ("human", "Tell me a joke about {topic}")
])

ai_msg_prompt.invoke({"topic": "beets"})

chain = ai_msg_prompt | llm
#chain.invoke({"topic": "beets"})
str_chain = chain | StrOutputParser()
result = str_chain.invoke({"topic": "beets"})
#print(result)
#for chunk in str_chain.stream({"topic": "beets"}):
#    print(chunk, end="|")

#

prompt = ChatPromptTemplate.from_messages([
  ("system", 'You know that the current date is "{current_date}".'),
  ("human", "{question}")
])

chain = prompt | llm | StrOutputParser()

#chain.invoke({
 # "question": "What is the current date?",
 # "current_date": date.today()
#})
#llm.invoke(
#    "What was the Old Ship Saloon's total revenue in Q1 2023?"
# )

SOURCE = """
Old Ship Saloon 2023 quarterly revenue numbers:
Q1: $174782.38
Q2: $467372.38
Q3: $474773.38
Q4: $389289.23
"""

rag_prompt = ChatPromptTemplate.from_messages([
    ("system", 'You are a helpful assistant. Use the following context when responding:\n\n{context}.'),
    ("human", "{question}")
])

rag_chain = rag_prompt | llm | StrOutputParser()

rag_chain.invoke({
    "question": "What was the Old Ship Saloon's total revenue in Q1 2023?",
    "context": SOURCE
})

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = getpass()
# os.environ["LANGCHAIN_PROJECT"] = "freeCodeCamp"

chain.invoke({
    "question": "What is the current date?",
    "current_date": date.today()
})

# Turn off debug mode for clarity
set_debug(False)

import asyncio

stream = chain.astream_events({
    "question": "What is the current date?",
    "current_date": date.today()
}, version="v1")

async def main():
    async for event in stream:
        print(event)
        print("-----")

asyncio.run(main()) 
