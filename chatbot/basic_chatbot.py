from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages # kind of reducer
from langgraph.checkpoint.memory import MemorySaver
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

checkpointer = MemorySaver()

# Create graph
graph = StateGraph(ChatState)

# Add node
graph.add_node('chat_node',chat_node)

# Add edges
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

# compile graph
chatbot = graph.compile(checkpointer=checkpointer)

# For downloading the Graph Image
# png_bytes = chatbot.get_graph().draw_mermaid_png()

# output_file = "chatbot/basic_chatbot.png"

# # Write the PNG to disk
# with open(output_file, "wb") as f:
#     f.write(png_bytes)

# initial_state = {
#     'messages' : [HumanMessage(content="What is the capital of India?")]
# }

# response = chatbot.invoke(initial_state)['messages'][-1].content

# print(response)

thread_id = '1'

while True:
    user_message = input("Type here : ")

    print("User : ", user_message)

    if user_message.strip().lower() in ['exit', 'quit', 'bye']:
        break

    config = {'configurable' : {'thread_id' : thread_id}}

    response = chatbot.invoke({'messages' : [HumanMessage(content=user_message)]},config=config)

    print('AI : ', response['messages'][-1].content)