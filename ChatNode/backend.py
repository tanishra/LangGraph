from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model='gpt-4o-mini')

# State 
class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]

# Node
def chat_node(state : ChatState):
    messages = state['messages']
    response = llm.invoke(messages)

    return {'messages' : [response]}

# Checkpointer 
checkpointer = InMemorySaver()

# Graph
graph = StateGraph()

# Add Nodes
graph.add_node('chat_node',chat_node)

# Add Edges
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

# Compile graph
chatbot = graph.compile(checkpointer=checkpointer)