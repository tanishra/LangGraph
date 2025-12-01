from langgraph.graph import START, END, StateGraph
from typing import TypedDict

class Batsman(TypedDict):
    runs : int
    balls : int
    fours : int
    sixes : int
    sr : float
    bpb : float
    boundary_percent : float
    summary : str

def calculate_sr(state : Batsman) -> Batsman:
    sr = (state['runs'] / state['balls']) * 100

    return {'sr' : sr}

def calculate_bpb(state : Batsman) -> Batsman:
    bpb = state['balls'] / (state['fours'] + state['sixes'])

    return {'bpb' : bpb}

def calculate_boundary_percent(state : Batsman) -> Batsman:
    boundary_percent = (((state['fours'] * 4) + (state['sixes'] * 6)) / state['runs']) * 100

    return {'boundary_percent' : boundary_percent} 

def calculate_summary(state : Batsman) -> Batsman:
    summary = f"""
    Strike Rate - {state['sr']} \n
    Balls per boundary - {state['bpb']} \n
    Boundary percent - {state['boundary_percent']}
    """

    return {'summary' : summary}

graph = StateGraph(Batsman)

graph.add_node('calculate_sr',calculate_sr)
graph.add_node('calculate_bpb',calculate_bpb)
graph.add_node('calculate_boundary_percent',calculate_boundary_percent)
graph.add_node('calculate_summary',calculate_summary)

graph.add_edge(START,'calculate_sr')
graph.add_edge(START,'calculate_bpb')
graph.add_edge(START,'calculate_boundary_percent')

graph.add_edge('calculate_sr','calculate_summary')
graph.add_edge('calculate_bpb','calculate_summary')
graph.add_edge('calculate_boundary_percent','calculate_summary')

graph.add_edge('calculate_summary',END)

workflow = graph.compile()

initial_state = {
    'runs' : 100,
    'sixes' : 5,
    'balls' : 50,
    'fours' : 6
}

final_state = workflow.invoke(initial_state)

print(final_state)

png_bytes = workflow.get_graph().draw_mermaid_png()

output_file = "parallel-workflow/cricket_workflow.png"

# Write the PNG to disk
with open(output_file, "wb") as f:
    f.write(png_bytes)


