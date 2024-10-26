from langchain.agents import tool
from agents.clients_agent import create_clients_agent
from agents.funds_agent import create_funds_agent
import config


@tool 
def ask_clients_agent(query:str):
    """This tool answers natural language questions about bank clients. Use the tool
    to find information about clients and their investments, like their personal data, 
    net worth, preferences and what in what funds they have invested."""

    agent = create_clients_agent()
    
    answer = agent.invoke({"input":query})

    for item in answer["intermediate_steps"]:
        item_str = f"CLIENT AGENT: {item[0].log}"
        config.model_reasoning.append(item_str)
        #config.model_reasoning += '\n' + item[1]
        #config.model_reasoning += "\n*****************"

    print(config.model_reasoning)
    return answer



@tool 
def ask_funds_agent(query:str):
    """This tool answers natural language questions about funds that a bank is offering. 
    Use the tool to find out quantitative and numeric data related to a specific fund, like 
    its annual yield, cumulative returns, etc., and also the description of each fund."""

    agent = create_funds_agent()

    answer = agent.invoke({"input":query})

    for item in answer["intermediate_steps"]:
        item_str = f"FUNDS AGENT: {item[0].log}" 
        config.model_reasoning.append(item_str)
        #config.model_reasoning += '\n' + item[1]
        #config.model_reasoning += "\n*****************"  

    print(config.model_reasoning)
    return answer