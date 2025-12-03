from langgraph.graph import START, END, StateGraph
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from typing import TypedDict, Literal, Annotated
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# TweetSchema
class TweetEvaluation(BaseModel):
    evaluation : Literal['Approved',"Needs_improvement"] = Field(...,description="Final evaluation result")
    feedback : str = Field(...,description="Feedback for the tweet")

# Can be same or different
generator = ChatOpenAI(model = 'gpt-4o-mini') 
evaluator = generator.with_structured_output(TweetEvaluation)
optimizer = ChatOpenAI(model = 'gpt-4o-mini')

# State
class TweetState(TypedDict):
    topic : str
    tweet : str
    evaluation : Literal['Approved',"Needs_improvement"]
    feedback : str
    iteration : int
    max_iteration : int

# Nodes Implementation
def generate_tweet(state : TweetState):
    # Prompt
    messages = [
        SystemMessage(content="You are a funny and clever Twitter/X influencer."),
        HumanMessage(content=f"""
        Write a short, original, and hilarious tweet on the topic : {state['topic']}.
        Rules:
        - Do not use question-answer format.
        - Max 250 characters.
        - Use observational humor, irony, sarcasm, or cultural reference.
        - Think in meme logic, punchlines, or relatable takes.
        - Use simple, day to day english.
        - This is version {state['iteration'] + 1} """)
    ]

    # Generate
    response = generator.invoke(messages).content

    return {'tweet' : response}

def evaluate_tweet(state : TweetState):
    # Prompt
    messages = [
        SystemMessage(content="You are a ruthless, no-laugh-given Twitter critic. You evaluate tweets baesd on humor, originality, virality, and tweet format"),
        HumanMessage(content=f"""
        Evaluate the following tweet : \n {state['tweet']} \n
        Use the criteria below to evaluate the tweet: 
        1. Originality - Is this fresh, or have you seen it a hundred times before?
        2. Humor - Did it genuinely make you smile, laugh, or chuckle ?
        3. Punchiness - Is it short, sharp, and scroll-stopping ?
        4. Virality Potential - Would people retweet or share it?
        5. Format - Is it a well-formed tweet (not a setup-punchline joke, not a Q&A joke, and under 250 characters) ?

        Auto-reject if:
        - It's written in question-answer format(e.g., "Why did .." or "what happens when..")
        - It exceeds 250 characters
        - It reads like a traditional setup-punchline joke
        - Don't end with generic, throwaway, or deflating lines that weaken the humor (e.g.., "Masterpieces of the auntie-uncle universe" or "vague summary")

        ### Respond ONLY is structured format : 
        - evaluation : "Approved" or "Needs_improvement"
        - feedback : One paragraph explaining the strengths and weaknesses""")
    ]

    # Evaluate
    response = evaluator.invoke(messages)

    return {'evaluation' : response.evaluation, "feedback" : response.feedback}

# Condition
def route_evaluation(state : TweetState):
    if state['evaluation'] == "Approved" or state['iteration'] <= state['max_iteration']: 
        return "Approved"
    else:
        return "Needs_improvment"

def optimize_tweet(state : TweetState):
    # Prompt
    messages = [
        SystemMessage(content="You punch up tweets for virality and humor based on given feedback."),
        HumanMessage(content=f"""
        Improve the tweet based on this feedback: {state['feedback']} \n
        topic : {state['topic']} \n Original tweet : {state['tweet']} \n

        Re-write it as a short, viral-worthy tweet. Avoid Q&A style and stay under 250 characters. """)
    ]

    # Optimize
    response = optimizer.invoke(messages).content
    iteration = state['iteration'] + 1

    return {'tweet' : response, 'iteration' : iteration}

# Graph
graph = StateGraph(TweetState)

# Add Nodes
graph.add_node('generate',generate_tweet)
graph.add_node('evaluate',evaluate_tweet)
graph.add_node('optimize',optimize_tweet)

# Add Edges
graph.add_edge(START,'generate')
graph.add_edge('generate','evaluate')
graph.add_conditional_edges('evaluate',route_evaluation,{'Approved': END,'Needs_improvement' : 'optimize'})
graph.add_edge('optimize','evaluate')

# Compile the graph
workflow = graph.compile()

# Execute
initial_state = {
    'topic' : "Black hole",
    'iteration' : 1,
    'max_iteration' : 5
}

final_state = workflow.invole(initial_state)

print(final_state)

png_bytes = workflow.get_graph().draw_mermaid_png()

output_file = "iterative-workflow/post-generation-workflow.png"

# Write the PNG to disk
with open(output_file, "wb") as f:
    f.write(png_bytes)