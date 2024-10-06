
from langchain_openai import ChatOpenAI
from typing import Literal
from langchain_core.tools import tool
from tools import get_circle_area,get_square_area
from langgraph.prebuilt import create_react_agent, chat_agent_executor


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
tools = [get_circle_area,get_square_area]
# Define the graph
graph = create_react_agent(model, tools=tools)

'''

def main():

    graph = create_graph()

    while True:
        question = input("What do you want?: ")
        inputs = {"messages": [("user", question)]}
        print_stream(graph.stream(inputs, stream_mode="values"))
    

if __name__ == "__main__":
    main()

'''