from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages # kind of reducer
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from typing import TypedDict, Annotated
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(model='gpt-4o-mini')

# Schema
class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]

# Node
def chat_node(state : ChatState):
    # Take user query from state
    messages = state['messages']

    # send to llm
    response = model.invoke(messages)

    return {"messages" : [response]}

# Create graph
graph = StateGraph(ChatState)

# Add node
graph.add_node('chat_node',chat_node)

# Add edges
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

# compile graph
chatbot = graph.compile()

png_bytes = chatbot.get_graph().draw_mermaid_png()

output_file = "chatbot/basic_chatbot.png"

# Write the PNG to disk
with open(output_file, "wb") as f:
    f.write(png_bytes)