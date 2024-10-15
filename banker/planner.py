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

    model_name = os.getenv("MODEL_NAME")
    #model_name ="claude-3-5-sonnet-20240620"
    print(f"\nPlanner is using {model_name}")

    prompt_template = """
            You're a planner that will tell an agent how to solve a request related to financial
            advice, using a set of tools. Thanks carefully about the steps to solve the question. 
            The output must be a numbered list of steps. 
            Questions will be in Spanish.
            These are the tools available to solve the question:
            - get_similar_clients to know what clients are similar to another
            - ask_clients_agent to know information about clients
            - ask_funds_agent, to get information about products
            - get client benefits to know the benefits of a client

            Examples:

            Question: Tell me the benefits of the client Pepita Perez
            Output: 1. Invoke the tool ask_clients_agent to know the ID of Pepita Perez
                    2. Invoke the tool get_client_benefits to get the benefits
                    3. Return the benefits to the user
                   
            Question: que clientes de más de 1000€ de patrimonio celebran su cumpleaños en la próxima semana
            Output: 1. Invocar a la herramienta ask_clients_agent para acceder a la base de datos y recuperar clientes que cumplen esa condicion
                    2. Devolver los clientes en formato JSON

            Question: dime que clientes con pocas inversiones con nosotros se parecen a otros clientes que sí son de alto patrimonio
            Output: 1. Invocar a la herramienta ask_portfolio_agent para averiguar el 10% del valor medio de las carteras
                    2. Invocar a la herramienta ask_portfolio_agent para sacar los codigos de los clientes que tengan una cartera de valor inferior. Nos quedamos con los 10 que tengan la cartera más baja.
                    3. Invocar a la herramienta get_similar_clients con un parametro que indique "alto patrimonio" con cada uno de los clientes encontrados y así obtener una lista de los clientes parecidos
                    4. Invocar la herramienta ask_clients_agent para obtener los nombres de esos clientes a partir de sus códigos
                    5. Devolver los clientes en formato JSON

            Question: dime qué clientes han manifestado interes por la inversión en "private equity"
            Output: 1. Invocar la herramienta ask_clients_agent para obtener qué clientes están interesados en ese tipo de inversion
                    2. Devolver los clientes en formato JSON

            Question: cuales de mis clientes estan ganado más de un 10% en lo que va de año
            Output: 1. Invocar la herramienta ask_portfolio_agent para obtener el listado de los clientes que cumplen esa condicion
                    2. Invocar la herramieinta ask_clients_agent para obtener los nombres de los clientes a partir de su código
                    3. Devolver los clientes en formato JSON

            Question: cuales de mis clientes estan ganado más de un 10% en lo que va de año y son inversores en productos estructurados
            Output: 1. Invocar la herramienta ask_portfolio_agent para obtener el listado de los codigos de los clientes que estén ganando más de un 10% e invierten en productos estructurados, y quedarse con los 30 que más ganan.
                    2. Invocar a la herramienta ask_clients_agent para obtener los nombres de esos clientes
                    3. Devolver los clientes en formato JSON

            Question: dame un listado con todos los clientes de fondos cuyas carteras estén mal diversifcadas y proponme una serie de operaciones para mejorar la situación
            Output: 1. Invocar la herramienta ask_clients_agent para obtener una lista de códigos de clientes que tienen fondos
                    2. Para cada cliente invocar a la herramienta get_portfolio_status.
                    3. Si el valor es bajo, significa que la cartera esta mal diversificada: invocar a la herramienta get_portfolio_improvements para la cartera de ese cliente
                    4. Devolver la lista de operaciones propuestas para cada cliente con una cartera mal diversificada en formato JSON


            The question to solve is {question}

            Begin!                
"""

    llm = ChatOpenAI(model_name=model_name, temperature=0)
    #llm = ChatAnthropic(model="claude-3-5-sonnet-20240620",temperature=0)

    prompt = ChatPromptTemplate.from_template(prompt_template)
    ouput_parser = StrOutputParser()

    chain = prompt | llm | ouput_parser

    result = chain.invoke({"question": question})
    return result

def main():

    main_agent = create_main_agent()

    while True:
        
        question = input("Introduce tu consulta: ")
        plan = define_plan(question)
        print(f"Plan sugerido:\n{plan}")

        config.model_call_cost = 0

        with get_openai_callback() as cb:
            main_agent.invoke({"input":question,"plan":plan})
            config.model_call_cost += cb.total_cost

            print(f"Total Cost (USD): ${config.model_call_cost}")

if __name__ == "__main__":
    main()