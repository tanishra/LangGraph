from langgraph.graph import START, END, StateGraph
from typing import TypedDict

# Define State
class BMI(TypedDict):
    weight : float # Kg
    height : float # meters
    category : str # Normal, Overweight, Underweight, Obese
    bmi : float


def calculate_bmi(state : BMI) -> BMI:
    weight = state['weight']
    height = state['height']

    bmi = weight / (height ** 2)

    state['bmi'] = round(bmi,2)

    return state

def label_category(state : BMI) -> BMI:
    bmi = state['bmi']

    if bmi < 18.5:
        state['category'] = "Underweight"
    elif 18.5 <= bmi < 25:
        state['category'] = "Normal"
    elif 25<= bmi < 30:
        state['category'] = "Overweight"
    else:
        state['category'] = "Obese"
    
    return state


# Define graph
graph = StateGraph(BMI)

# Add nodes
graph.add_node('calculate_bmi',calculate_bmi)
graph.add_node('label_category',label_category)

# Add edges
graph.add_edge(START,'calculate_bmi')
graph.add_edge('calculate_bmi','label_category')
graph.add_edge('label_category',END)

# Compile the graph
workflow = graph.compile()

# Execute the graph
initial_state = {"weight" : 65,"height" : 1.52}

final_state = workflow.invoke(initial_state)

print(final_state)