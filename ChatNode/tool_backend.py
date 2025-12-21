from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated
from dotenv import load_dotenv
import sqlite3
import os
import requests

load_dotenv()

EURI_API = os.getenv("EURI_API_KEY")
api_key = os.getenv("ALPHAVANTAGE_API_KEY")

# LLM
llm = ChatOpenAI(model='gpt-4.1-mini')

# Tools
search_tool = DuckDuckGoSearchRun(region='us-en')

@tool
def calculator(first_num : float, second_num : float, operation : str) -> dict:
    """
    Perform basic arithmetic operation on two numbers.
    Supported Operations : add, sub, mul, div
    """

    try:
        if operation == 'add':
            result = first_num + second_num
        elif operation == 'sub':
            result = first_num - second_num
        elif operation == 'mul':
            result = first_num * second_num
        elif operation == 'div':
            if second_num == 0:
                return {'error' : "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {'error' : f'Unsupported operation {operation}'}
        return {'firstnum' : first_num, 'second_num' : second_num, 'operation' : operation, 'result' : result}
    except Exception as e:
        return {'error' : str(e)}
    
@tool
def get_stock_price(symbol : str) -> dict:
    """
    Fetch latest stock price for a given symbol using Alpha vantage API.
    """ 

    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    result = requests.get(url)

    return result.json()

tools = [search_tool,calculator,get_stock_price]
llm_with_tools = llm.bind_tools(tools)

# State 
class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]

# Node
def chat_node(state : ChatState):
    messages = state['messages']
    response = llm.invoke(messages)

    return {'messages' : [response]}

tool_node = ToolNode(tools)

# Sqlite database connection
conn = sqlite3.connect(database='chatbot.db',check_same_thread=False)

# Checkpointer 
checkpointer = SqliteSaver(conn=conn)

# Graph
graph = StateGraph(ChatState)

# Add Nodes
graph.add_node('chat_node',chat_node)
graph.add_node('tools',tool_node)

# Add Edges
graph.add_edge(START,'chat_node')
graph.add_conditional_edges('chat_node',tools_condition)
graph.add_edge('tools','chat_node') 

# Compile graph
chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    thread_ids = set()
    for checkpoint in checkpointer.list(None):
        thread_ids.add(checkpoint.config['configurable']['thread_id'])

    return list(thread_ids)