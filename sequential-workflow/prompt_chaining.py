from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from typing import TypedDict

load_dotenv()

model = ChatOpenAI()

# Create a state
class BlogState(TypedDict):
    title : str
    outline : str
    content : str

def create_outline(state : BlogState) -> BlogState:
    # Fetch title
    title = state['title']

    # call llm gen outline
    prompt = f"Generate a detailed outline for a blog on the topic - {title}"
    outline = model.invoke(prompt).content

    # update state
    state['outline'] = outline
    return state

def create_blog(state : BlogState) -> BlogState:
    title = state['title']
    outline = state['outline']

    prompt = f"Write a detailed blog on the title - {title} using the following outline \n {outline}"

    content = model.invoke(prompt).content

    state['content'] = content

    return state

# Create a graph
graph = StateGraph(BlogState)

# Add nodes
graph.add_node('create_outline',create_outline)
graph.add_node('create_blog',create_blog)

# Add edges
graph.add_edge(START,'create_outline')
graph.add_edge('create_outline','create_blog')
graph.add_edge('create_blog',END)

# Compile the graph
workflow = graph.compile()

# Execute the graph
initial_state = {"title" : "BlackHole"}

final_state = workflow.invoke(initial_state)

print(final_state)