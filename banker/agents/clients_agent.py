
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI, OpenAI
from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv

from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)

examples = [
    {
        "input": "Find clientes with net worth over 20000",
        "query": "SELECT name,surname,net_worth FROM clients WHERE net_worth > 20000;",
    },
    {
        "input": "Tell me the average net worth of clients under 30 years old",
        "query": "select avg(net_worth) from clients where (julianday('now') - julianday(birthday)) / 365.25 < 30;",
    },
    {
        "input": "Tell me the percentage of clients interested in invest in crytpcurrencies",
        "query": "select (count(case when preferences like '%cryptocurrency%' then 1 END) * 100.0 / count(*)) from clients;",
    },
    {
        "input": "Tell me the names of the customers whose birthdays are this week and who have a net worth of more than 20,000 euros",
        "query": "select dni,name,surname,birthdate from clients where strftime('%W',birthday) = strftime('%W','now') and net_worth > 20000;",
    },
    {
        "input": "What five clients have the greater net worth",
        "query": "SELECT name, surname, net_worth from clients ORDER BY net_worth DESC LIMIT 5;",
    },
    {
        "input": "Tell me five clients interested in investing in real estate and with net worth over 200000",
        "query": "SELECT name, surname, net_worth FROM clients where preferences like '%real estate%' ORDER BY net_worth DESC LIMIT 5;",
    },
    {
        "input": "Tell me the name of the client with DNI 46900104E",
        "query": "SELECT name, surname FROM clients WHERE DNI == '46900104E';"
    },

]


def create_clients_agent():

    load_dotenv()

    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples,
        OpenAIEmbeddings(),
        FAISS,
        k=5,
        input_keys=["input"],
    )

    system_prefix = """You are an agent designed to interact with a SQL database that contains information about clients of a bank.
    Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
    If the user doesn't specify the number of results, limit your query to at most 30 results.
    You can order the results by a relevant column to return the most interesting examples in the database.
    Never query for all the columns from a specific table, only ask for the relevant columns given the question.
    You have access to tools for interacting with the database.
    Only use the given tools. Only use the information returned by the tools to construct your final answer.
    You MUST double check your query before executing it. If you get an error while executing a query, 
    rewrite the query and try again.


    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.


    Here are some examples of user inputs and their corresponding SQL queries:"""

    few_shot_prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=PromptTemplate.from_template(
            "User input: {input}\nSQL query: {query}"
        ),
        input_variables=["input"],
        partial_variables={"dialect":"sqlite"},
        prefix=system_prefix,
        suffix="",
    )

    full_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate(prompt=few_shot_prompt),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    db = SQLDatabase.from_uri("sqlite:///data/dbclients.db")
    model_name = os.getenv("MODEL_NAME")
    print(f"\nClient Agent is using {model_name}")
    llm = ChatOpenAI(model=model_name,temperature=0)
    agent = create_sql_agent(
        llm=llm,
        db=db,
        prompt=full_prompt,
        verbose=True,
        agent_type="openai-tools",
    )

    return agent

if __name__ == "__main__":
    
    client_agent = create_clients_agent()
    client_agent.invoke({"input": "Describe el esquema de la tabla clientes"})

