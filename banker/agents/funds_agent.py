from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)

def create_funds_agent():

    load_dotenv()

    db = SQLDatabase.from_uri("sqlite:///data/dbfunds.db")
    llm = ChatOpenAI(model="gpt-4o",temperature=0)
    print("Using gpt-4o")
    agent = create_sql_agent(
        llm=llm,
        db=db,
        verbose=True,
        agent_type="openai-tools",
        agent_executor_kwargs={"return_intermediate_steps":True}
    )

    return agent

def main():

    funds_agent = create_funds_agent()

    while True:
        query = input("Type yor query: ")
        result = funds_agent.invoke({"input":query})
        print(result['output'])
        for item in result["intermediate_steps"]:
            print(item[0].log)
            print(item[1])
            print("***************")

if __name__ == "__main__":
    main()