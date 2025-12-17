from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from Custom_Chat_Model import EuriChatModel
from typing import TypedDict, Annotated
from dotenv import load_dotenv
import sqlite3
import os

load_dotenv()

EURI_API = os.getenv("EURI_API_KEY")

llm = EuriChatModel(
    model='gpt-4.1-mini',
    api_key=EURI_API
    )

# State 
class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]

# Node
def chat_node(state : ChatState):
    messages = state['messages']
    response = llm.invoke(messages)

    return {'messages' : [response]}

# Sqlite database connection
conn = sqlite3.connect(database='chatbot.db',check_same_thread=False)

# Checkpointer 
checkpointer = SqliteSaver(conn=conn)

# Graph
graph = StateGraph(ChatState)

# Add Nodes
graph.add_node('chat_node',chat_node)

# Add Edges
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

# Compile graph
chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    
    return list(all_threads)