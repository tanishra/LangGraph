from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict
import time

# Define State
class CrashState(TypedDict):
    input : str
    step1 : str
    step2 : str
    step3 : str

# Define Nodes
def step_1(state: CrashState) -> CrashState:
    print("Step 1 Executed")
    return {'step1' : "done", 'input' : state['input']}

def step_2(state: CrashState) -> CrashState:
    print("Step 2 hanging .... now manually interrupt from the terminal(Stop button)")
    time.sleep(30)
    return {'step2' : "done"}

def step_3(state: CrashState) -> CrashState:
    print("Step 3 Executed")
    return {'step3' : "done"}


# Define the graph
graph = StateGraph(CrashState)

# Add nodes
graph.add_node('step_1',step_1)
graph.add_node('step_2',step_2)
graph.add_node('step_3',step_3)

# Add edges
graph.add_edge(START,'step_1')
graph.add_edge('step_1','step_2')
graph.add_edge('step_2','step_3')
graph.add_edge('step_3',END)

# Checkpointer
checkpointer = InMemorySaver()

# Compile the graph
workflow = graph.compile(checkpointer=checkpointer)

try:
    print("Running graph: Please manually interrupt during Step - 2 ....")
    workflow.invoke({'input' : "start"},config={'configurable' : {'thread_id' : '1'}})
except KeyboardInterrupt:
    print("Kernel manually interrupted (crash simulated)")

print(workflow.get_state(config={'configurable' : {'thread_id' : '1'}}))

print(workflow.get_state_history(config={'configurable' : {'thread_id' : '1'}}))

final_state = workflow.invoke(None,config={'configurable' : {'thread_id' : '1'}})
print("Final state",final_state)