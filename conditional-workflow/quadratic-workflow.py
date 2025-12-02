from langgraph.graph import START, END, StateGraph
from typing import TypedDict, Literal

class QuadState(TypedDict):
    a : int
    b : int
    c : int
    equation : str
    discriminant : str
    result : str


def show_equation(state : QuadState):
    equation = f"{state['a']}x^2 + {state['b']}x + {state['c']}"

    return {'equation' : equation}

def calculate_discriminant(state : QuadState):
    disciminant = state['b'] ** 2 - (4 * state['a'] * state['c'])

    return {'discriminant' : disciminant}

def real_roots(state : QuadState):
    root1 = (-state['b'] + state['discriminant'] ** 0.5)/ (2 * state['a'])
    root2 = (-state['b'] - state['discriminant'] ** 0.5)/ (2 * state['a'])

    result = f"The roots are {root1} and {root2}"

    return {'result' : result}

def repeated_roots(state : QuadState):
    root = (-state['b']) / (2 * state['a'])

    result = f"Only repeating root is {root}"

    return {'result' : result}

def no_real_roots(state : QuadState):
    result = f"No real roots exist"

    return {'result' : result}

def check_condition(state : QuadState) -> Literal['real_roots','repeated_roots','no_real_roots']:
    if state['discriminant'] > 0:
        return 'real_roots'
    elif state['discriminant'] == 0:
        return 'repeated_roots'
    else:
        return 'no_real_roots'

graph = StateGraph(QuadState)

graph.add_node('show_equation',show_equation)
graph.add_node('calculate_discriminant',calculate_discriminant)
graph.add_node('real_roots',real_roots)
graph.add_node('repeated_roots',repeated_roots)
graph.add_node('no_real_roots',no_real_roots)

graph.add_edge(START,'show_equation')
graph.add_edge('show_equation','calculate_discriminant')
graph.add_conditional_edges('calculate_discriminant',check_condition)
graph.add_edge('real_roots',END)
graph.add_edge('repeated_roots',END)
graph.add_edge('no_real_roots',END)

workflow = graph.compile()

initial_state = {
    'a' : 4,
    'b' : -5,
    'c' : -4
}

final_state = workflow.invoke(initial_state)

print(final_state)

png_bytes = workflow.get_graph().draw_mermaid_png()

output_file = "conditional-workflow/quadratic-workflow.png"

# Write the PNG to disk
with open(output_file, "wb") as f:
    f.write(png_bytes)