from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage, BaseMessage
from typing import TypedDict, Annotated
from dotenv import load_dotenv

load_dotenv()

# LLM
llm = ChatOpenAI(model='gpt-4.1-mini')

# Document Loader
loader = PyPDFLoader('System Design Playbook.pdf')
docs = loader.load()

# Splitter
splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
chunks = splitter.split_documents(docs)

# Embeddings
embeddings = OpenAIEmbeddings(model='text-embedding-3-small')

# Vector Store
vector_store = FAISS.from_documents(chunks,embeddings)

# Retriever
retriever = vector_store.as_retriever(search_type='similarity',search_kwargs={'k' : 4})

# Tool
@tool
def rag_tool(query):
    """
    Retrieve relevant information from the pdf document.
    Use this tool when the user asks factual / conceptual questions that might be answered from the stored documents.
    """

    result = retriever.invoke(query)

    context = [doc.page_content for doc in result]
    metadata = [doc.metadata for doc in result]

    return {
        'query' : query,
        'context' : context,
        'metadata' : metadata
    }

# Tool Binding
tools = [rag_tool]
llm_with_tools = llm.bind_tools(tools)

# State Definition
class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]

# Nodes
def chat_node(state : ChatState):
    messages = state['messages']

    response = llm_with_tools.invoke(messages)

    return {'messages' : response}

tool_node = ToolNode(tools)

# Graph
graph = StateGraph(ChatState)

graph.add_node('chat_node',chat_node)
graph.add_node('tool_node',tool_node)

graph.add_edge(START,'chat_node')
graph.add_conditional_edges('chat_node',tools_condition)
graph.add_edge('tool_node','chat_node')

chatbot = graph.compile()

result = chatbot.invoke(
    {
        'messages' : [HumanMessage(content=("Using the pdf, Explain how amazon s2 achieves 99.99 percent durability?"))]
    }
)

print(result['messages'][-1].content)