from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_community.callbacks import get_openai_callback


from tools.clients.client_tools import get_similar_clients
from tools.agent_tools import ask_clients_agent, ask_funds_agent


from dotenv import load_dotenv
import os
import config

def create_main_agent():

    load_dotenv()

    tools = [get_similar_clients, ask_clients_agent, ask_funds_agent]

    react_template = """You are a financial assistant.
    Answer the following questions as best you can, taking into account this plan
     {plan} 
     
     You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question, 

Begin!

{chat_history}
Question: {input}
Thought:{agent_scratchpad}"""

    
    react_prompt = PromptTemplate.from_template(react_template)

    # Added input_key and output_key params because the extra {plan} variable in the prompt. TODO: why?
    # You need to add set the input_key when you define your memory so that the memory save_context method knows 
    # where to place the user input. If not, arises an error because there's ambiguity about whether "input" or "plan" 
    # are the keys that should contain the new user input.
    memory = ConversationBufferMemory(memory_key="chat_history", input_key="input", output_key='output')

    # Choose the LLM to use
    llm = ChatOpenAI(model="gpt-4o",temperature=0)
    
    # Construct the ReAct agent
    main_agent = create_react_agent(llm, tools, react_prompt)

    # Create an agent executor by passing in the agent and tools
    agent_executor = AgentExecutor(agent=main_agent, 
                                   tools=tools, 
                                   memory=memory,
                                   verbose=True, 
                                   handle_parsing_errors=True,
                                   return_intermediate_steps=True)
    
    return agent_executor

    

def main():

    #query = "Para la cliente Bernardita Mora, ¿es mejor invertir en bitcoins o en el IBEX"
    #query = "Dame como maximo cinco clientes con nivel adquisitivo alto, que tengan entre 20 años y 30 años y que sean residentes en España"
    #query = "Haze un resumen del portfolio de Bernardita Mora"
    #query = "Que producto es mejor para Bernardita Mora: el producto DB CONSERVADOR ESG con el producto DB CORTO PLAZO"
    #query = "buscame un fondo de inversion que invierta en china"
    #query = "Calculame el ratio de Sharpe del producto DB CONSERVADOR ESG"
    #query = "Sácame un listado con todos aquellos clientes con propensión a productos estructurados \
     #   que tengan un perfil de riesgo 3 o superior y a cuya cartera le falte inversión en bolsa americana."

    main_agent = create_main_agent()
    config.model_call_cost = 0

    while True:
        query = input("Type your query: ")
        config.model_call_cost = 0
        with get_openai_callback() as cb:
            main_agent.invoke({"input":query,"plan":"think step by step"})
            config.model_call_cost += cb.total_cost

            print(f"Total Cost (USD): ${config.model_call_cost}")


if __name__ == "__main__":
    main()