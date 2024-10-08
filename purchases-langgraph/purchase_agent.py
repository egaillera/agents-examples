from ast import Dict
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

from extraction_agent import execute_extractor


def extract_purchase(query:str):

    products = execute_extractor(query)

    #products = [{"type":"jamon","quality":"iberico"},{"type":"queso cabra","quality":None}]
    
    return products

class OverallState(TypedDict):
    request:str
    products:Dict
    saved:str

class InputState(TypedDict):
    request: str

def extraction_node(state: OverallState):
    print("-- Extraction Node --")
    print(state)
    return {"products":extract_purchase(state["request"])}

def purchase_node(state: OverallState):
    print("-- Purchase Node --")
    print(state)
    return{"saved":"ok"}

builder = StateGraph(InputState)
builder.add_node("extraction_node",extraction_node)
builder.add_node("purchase_node",purchase_node)
builder.add_edge(START,"extraction_node")
builder.add_edge("extraction_node","purchase_node")
builder.add_edge("purchase_node",END)

graph = builder.compile()

graph.invoke({"request":"quiero lomo iberico embuchado"})
