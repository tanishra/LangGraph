from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI()

# Define the State
class LLMState(TypedDict):
    question : str
    answer : str


def llm_qa(state : LLMState) -> LLMState:
    # Extract the question from the state
    question = state['question']

    # Form a prompt
    prompt = f"Answer the following question {question}"

    # Ask the question to LLM
    answer = model.invoke(prompt).content

    # Update the state
    state['answer'] = answer

    return state

# Define the graph 
graph = StateGraph(LLMState)

# Add the nodes
graph.add_node('llm_qa',llm_qa)

# Add the edges
graph.add_edge(START,'llm_qa')
graph.add_edge('llm_qa',END)

# Compile the graph
workflow = graph.compile()

# Execute the graph
initial_state = {"question" : "Who is the prime minister of India?"}
final_state = workflow.invoke(initial_state)

print(final_state)
