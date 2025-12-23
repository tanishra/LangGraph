from langgraph.graph import START, END, StateGraph
from langchain_openai import ChatOpenAI
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()

# LLM
subgraph_llm = ChatOpenAI(model='gpt-4.1-mini')
parent_llm = ChatOpenAI(model='gpt-4o-mini')

# State
class ParentState(TypedDict):
    question : str
    eng_answer : str
    hin_answer : str

# Node
def translate_text(state : ParentState):
    prompt = f"""Translate the following text into Hindi. Keep it natural and clear. Do not add extra content.
                Text : {state['input_text']}""".strip()
    
    translated_text = subgraph_llm.invoke(prompt).content

    return {'translated_text' : translate_text}

def generate_answer(state : ParentState):
    prompt = f"""You are a helpful assistant. Answer clearly. \n \n
                Question : {state['question']}"""
    
    answer = parent_llm.invoke(prompt).content

    return {'eng_answer' : answer}

# Sub-graph
subgraph_builder = StateGraph(ParentState)

subgraph_builder.add_node('translate_text',translate_text)

subgraph_builder.add_edge(START,'translate_text')
subgraph_builder.add_edge('translate_text',END)

subgraph = subgraph_builder.compile()

# Parent Graph
parent_builder = StateGraph(ParentState)

parent_builder.add_node('generate_answer',generate_answer)
parent_builder.add_node('translate_answer',subgraph)

parent_builder.add_edge(START,'generate_answer')
parent_builder.add_edge('generate_answer','translate_answer')
parent_builder.add_edge('translate_answer',END)

# Compile
parentgraph = parent_builder.compile()

result = parentgraph.invoke({'question' : "What is a blackhole?"})

print(result)