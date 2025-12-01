from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph
from typing import TypedDict, Annotated
from pydantic import BaseModel, Field
import operator
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(model='gpt-4o-mini')

class EvaluationSchema(BaseModel):
    feedback : str = Field(description="Detailed feedback for the essay")
    score : int = Field(description="Score out of 10",ge=0,le=10)

structured_model = model.with_structured_output(EvaluationSchema)

class UPSC(TypedDict):
    essay : str
    language_feedback : str
    analysis_feedback : str # Depth of analysis
    clarity_feedback : str # Clarity of thought
    overall_feedback : str
    individual_scores : Annotated[list[int],operator.add]
    avg_score : float

def evaluate_language(state : UPSC) -> UPSC:
    prompt = f"Evaluate the language quality of the following essay and provide a feedback and assign a score out of 10 \n {state['essay']}"

    output = structured_model.invoke(prompt)

    return {
        'language_feedback' : output.feedback,
        'individual_scores' : [output.score]
    }

def evaluate_analysis(state : UPSC) -> UPSC:
    prompt = f"Evaluate the depth of analysis of the following essay and provide a feedback and assign a score out of 10 \n {state['essay']}"

    output = structured_model.invoke(prompt)

    return {
        'analysis_feedback' : output.feedback,
        'individual_scores' : [output.score]
    }

def evaluate_thought(state : UPSC) -> UPSC:
    prompt = f"Evaluate the clarity of thought of the following essay and provide a feedback and assign a score out of 10 \n {state['essay']}"

    output = structured_model.invoke(prompt)

    return {
        'clarity_feedback' : output.feedback,
        'individual_scores' : [output.score]
    }

def final_evaluation(state : UPSC) -> UPSC:
    # summary feedback
    prompt = f"Based on the following feedbacks, create a summarized feedback \n  Language feedback - {state['language_feedback']} \n Depth of Analysis feedback - {state['analysis_feedback']} \n Clarity of thought feedback - {state['clarity_feedback']}"

    overall_feedback = model.invoke(prompt).content

    # avg calculate
    avg_score = sum(state['individual_scores']) / len(state['individual_scores'])

    return {
        'overall_feedback' : overall_feedback,
        'avg_score' : avg_score
    }

graph = StateGraph(UPSC)

graph.add_node('evaluate_language',evaluate_language)
graph.add_node('evaluate_analysis',evaluate_analysis)
graph.add_node('evaluate_thought',evaluate_thought)
graph.add_node('final_evaluation',final_evaluation)

graph.add_edge(START,'evaluate_language')
graph.add_edge(START,'evaluate_analysis')
graph.add_edge(START,'evaluate_thought')

graph.add_edge('evaluate_language','final_evaluation')
graph.add_edge('evaluate_analysis','final_evaluation')
graph.add_edge('evaluate_thought','final_evaluation')

graph.add_edge('final_evaluation',END)

workflow = graph.compile()

essay = """
A black hole is one of the most fascinating and extreme objects in the universe. It forms when a massive star exhausts its nuclear fuel and collapses under its own gravity. This collapse compresses the star's core into an incredibly dense point called a singularity, where gravity becomes so strong that nothing—not even light—can escape. The boundary surrounding this region is known as the event horizon. Once anything crosses this threshold, it is pulled inevitably inward.
Black holes are often imagined as cosmic vacuum cleaners, but they do not indiscriminately swallow everything around them. Instead, they influence nearby matter through their intense gravitational pull. Gas, dust, and even stars can orbit a black hole, forming a swirling accretion disk that heats up and emits powerful radiation.
Although black holes cannot be observed directly, scientists detect them by studying this radiation and the motion of nearby objects. In recent years, breakthroughs like the first image of a black hole's shadow have offered a glimpse into these mysterious giants. Black holes challenge our understanding of physics, especially when it comes to gravity, space, and time. Their study continues to push the boundaries of human knowledge, making them essential subjects in modern astrophysics.
"""

initial_state = {
    'essay' : essay
}

png_bytes = workflow.get_graph().draw_mermaid_png()

output_file = "parallel-workflow/upsc_workflow.png"

# Write the PNG to disk
with open(output_file, "wb") as f:
    f.write(png_bytes)

final_state = workflow.invoke(initial_state)

print(final_state)