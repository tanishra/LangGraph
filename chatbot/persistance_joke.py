from langgraph.graph import START, END, StateGraph
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(model='gpt-4o-mini')

# State of joke
class JokeState(TypedDict):
    joke : str
    topic : str
    explanation : str

# Define nodes
def generate_joke(state : JokeState):
    prompt = f"Generate a joke on the topic {state['topic']}"
    response = model.invok(prompt).content

    return {'joke' : response}

def generate_explanation(state : JokeState):
    prompt = f"Write an explanation for the joke - {state['joke']}"
    response = model.invoke(prompt).content

    return {'explanation' : response}

# Create graph
graph = StateGraph(JokeState)

# Add nodes
graph.add_node('generate_joke',generate_joke)
graph.add_node('generate_explanation',generate_explanation)

# Add edges
graph.add_edge(START,'generate_joke')
graph.add_edge('generate_joke','generate_explanation')
graph.add_edge('generate_explanation',END)

# Checkpointer 
checkpointer = InMemorySaver()

# Compile the graph
workflow = graph.compile(checkpointer=checkpointer)

# Execute the workflow
config1 = {'configurable' : {"thread_id" : "1"}}
initial_state = {'topic' : 'Black Hole'}
final_state = workflow.invoke(initial_state,config=config1)

print(final_state)

# print(workflow.get_state(config=config1)) # For final state checkpoint
# print(workflow.get_state_history(config=config1)) # For intermediate state checkpoint