from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, AnyMessage, BaseMessage
from typing import TypedDict, Annotated
from dotenv import load_dotenv

load_dotenv()

# LLM
llm = ChatOpenAI(model='gpt-4.1-mini')

# State
class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]

# Node 
def chat_node(state : ChatState):
    decision = interrupt({
        'type' : 'approval',
        'reason' : 'Model is about to answer a user question.',
        'question' : state['messages'][-1].content,
        'instruction' : "Approve this question? yes/no"
    })

    if decision['approved'] == 'no':
        return {'messages'  : AIMessage(content='Not Approved')}
    else:
        response = llm.invoke(state['messages'])
        return {'messages' : [response]}
    
# graph
graph = StateGraph(ChatState)

# add node
graph.add_node('chat_node',chat_node)

# add edges
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

# checkpointer is required for interrupt
checkpointer = MemorySaver()

# compile the graph
workflow = graph.compile(checkpointer=checkpointer)

config = {'configurable' : {'thread_id' : '123'}}

initial_state = {
    'messages' : 
    [
        ('user', 'Explain black hole in simple terms' )
    ]
}

result = workflow.invoke(initial_state,config=config)

message = result['__interrupt__'][0].value

print(message)

user_input = input(f"Backend message -  {message} \n Approve this question? (y/n) : ")

final_result = workflow.invoke(
    Command(resume={'approved' : user_input}),
    config=config
)

print(final_result)