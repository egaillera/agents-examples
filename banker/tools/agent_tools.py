from langchain.agents import tool
from agents.markets_agent import create_market_agent
from agents.clients_agent import create_clients_agent
from agents.portfolio_agent import create_portfolio_agent
from agents.product_agent import create_product_agent
from agents.recommendations_agent import create_recommendations_agent
from agents.funds_agent import create_funds_agent
from langchain_community.callbacks import get_openai_callback
import config

   

@tool 
def ask_clients_agent(query:str):
    """This tool answers natural language questions about bank clients. Use the tool
    to find information about clients and their portfolios, like their personal data, 
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
    Use the tool to find out cuantitive and numeric data related to a specific fund, 
    like its rentabilities, volatility, etc."""

    agent = create_funds_agent()

    answer = agent.invoke({"input":query})

    for item in answer["intermediate_steps"]:
        item_str = f"FUNDS AGENT: {item[0].log}" 
        config.model_reasoning.append(item_str)
        #config.model_reasoning += '\n' + item[1]
        #config.model_reasoning += "\n*****************"  

    print(config.model_reasoning)
    return answer