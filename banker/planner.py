from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks import get_openai_callback
from main_agent import create_main_agent
from dotenv import load_dotenv
import os
import config

def define_plan(question):
    load_dotenv()

    prompt_template = """
            You're a planner that will tell an agent how to solve a request related to financial
            advice, using a set of tools. Thanks carefully about the steps to solve the question. 
            The output must be a numbered list of steps. 
            Question and answers should be in English.
            These are the tools available to solve the question:
            - get_similar_clients to know what clients are similar to another
            - ask_clients_agent to know information about clients
            - ask_funds_agent, to get information about products

            Examples:

            Question: Tell me the 5 clients with more net worth that are investing in BBVA funds
            Output: 1. Invoke the tool ask_funds_agent to know the ISIN of BBVA funds
                    2. Invoke the tool ask_client_agent to know the top 5 clients that invest in those funds order by net worth
                    3. Return the name, the surname, the net worth of those clients to the user
                   
            Question: how much money has made Isidoro Toro in the last three months
            Output: 1. Invoke the tool ask_client_agent to know in which funds he has invested and how much
                    2. Use the tool ask_funds_agent to know the percentage of the cumulative return in 3 months of those funds
                    3. Calculate the benefit using the amount invested in each fund and the percentage of the acumulative return

            Question: find the client who has invested the most, and tell me three clients that are similar and how much are investing 
            Output: 1. Invoke the tool ask_client_agent to know the client who has invest the most and get his DNI
                    2. Invoke the tool get_similar clients to know three clients similar to the prior one
                    3. Invoke the tool ask_client_agent to know thier name and their surname, 
                    4. Invoke the tool ask_client_agent to know how much they have invested
                    6. Finally, return a list with the name and surname of each client and how much they have invested

            Question: Tell me which clients have shown interest in investing in private equity.
            Output: 1. Invoke the tool ask_clients_agent to get what clients are interested in this kind of investment
                    2. Return name and surname of those clients

            The question to solve is {question}

            Begin!                
"""

    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

    prompt = ChatPromptTemplate.from_template(prompt_template)
    ouput_parser = StrOutputParser()

    chain = prompt | llm | ouput_parser

    result = chain.invoke({"question": question})
    return result

def main():

    main_agent = create_main_agent()

    while True:
        
        question = input("Type your request: ")
        plan = define_plan(question)
        #print(f"Plan sugerido:\n{plan}")

        config.model_call_cost = 0

        with get_openai_callback() as cb:
            main_agent.invoke({"input":question,"plan":plan})
            config.model_call_cost += cb.total_cost

            print(f"Total Cost (USD): ${config.model_call_cost}")

if __name__ == "__main__":
    main()