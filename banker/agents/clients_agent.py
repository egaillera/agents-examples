
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
        "query": "select avg(net_worth) from clients where (strftime('%Y','now') - birth_year) > 30;",
    },
    {
        "input": "Tell me the percentage of clients interested in invest in cryptocurrency",
        "query": "select (count(case when preferences like '%cryptocurrency%' then 1 END) * 100.0 / count(*)) from clients;",
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

    db = SQLDatabase.from_uri("sqlite:///data/dbclients.db")
    llm = ChatOpenAI(model="gpt-4o",temperature=0)
    agent = create_sql_agent(
        llm=llm,
        db=db,
        verbose=True,
        agent_type="openai-tools",
        agent_executor_kwargs={"return_intermediate_steps":True}
    )

    return agent

if __name__ == "__main__":
    
    clients_agent = create_clients_agent()

    while True:
        query = input("Type yor query: ")
        result = clients_agent.invoke({"input":query})
        print(result['output'])
        for item in result["intermediate_steps"]:
            print(item[0].log)
            print(item[1])
            print("***************")

