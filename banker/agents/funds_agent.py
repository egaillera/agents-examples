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

examples = [
    {   "input": "Show me funds comercialized by BBVA", 
         "query": "select name, description from funds where name like '%BBVA%';"
    },
    {
        "input": "Find all funds with assets under management over 20000 euros",
        "query": "select name, assets_under_management FROM funds WHERE assets_under_management > 20000;",
    },
    {
        "input": "Tell me the average assets under managment of the BBVA funds",
        "query": "select avg(assets_under_management) from funds where name like '%BBVA%';",
    },
    {
        "input": "Tell me the funds with average return over 1% and with minium investment below 1000€",
        "query": "select name,average_return, minimum_investment from funds where average_return > 1 and minimum_investment < 1000;",
    },
    {
        "input": "Tell me which funds have a volatility greater than 0.1% and and average return gerater than 1 per cent",
        "query": "select name, volatility, average_return from funds where volatility > 0.1 and average_return > 1;",
    },
    {
        "input": "Tell me funds that invest in IICs",
        "query": "select name, description from funds where description like '%IIC%';",
    },
    {
        "input": "what funds that invest in ICCs have an average rentabiity greater than 0.5%",
        "query": "select name,average_return from funds where description like '%IIC%' and average_return > 0.5;",
    },
    {
        "input": "tell me funds with a cumulative return in the last three months greater than two per cent",
        "query": 'select name, return from funds inner join cumulative_return on funds.isin = cumulative_return.isin where period = "3 months" and return > 2;',
    },
    {
        "input": "tell me what funds have a cumulative return in the last month less than one per cent",
        "query": 'select name, return from funds inner join cumulative_return on funds.isin = cumulative_return.isin where period = "1 month" and return < 1;',
    },
    {
        "input": "tell me what funds have loses in the last five years",
        "query": 'select name, return from funds inner join cumulative_return on funds.isin = cumulative_return.isin where period = "5 years" and return < 0;',
    },
    {
        "input": "calcuate the average loses of the funds that hast lost money in the last three years",
        "query": 'select avg(return) from cumulative_return where period = "3 years" and return < 0;',
    },
    {
        "input": "calculate the average of the loses of the BBVA fund that has lost money in the last year",
        "query": "select avg(return) from funds inner join cumulative_return on funds.isin = cumulative_return.isin where period = '1 year' and return < 0 and name like '%BBVA%';",
    },
    {
        "input": "tell me what funds make more than 20% during 2023",
        "query": "select name,annual_yield from funds inner join annual_return on funds.isin = annual_return.isin where year = '2023' and annual_yield > 20 and annual_yield not null;",
    },
    {
        "input": "tell me what funds are working well this year",
        "query": "select name,annual_yield from funds inner join annual_return on funds.isin = annual_return.isin where year = '2024' order by annual_yield desc limit 10;",
    },
    {
        "input": "tell me what funds that invest in european stocks are working well in the last three months",
        "query": "select name, return from funds inner join cumulative_return on funds.isin = cumulative_return.isin where period = '3 months' and description like '%europ%' and return not null order by return desc limit 10;",
    },

]


def create_funds_agent():

    load_dotenv()

    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples,
        OpenAIEmbeddings(),
        FAISS,
        k=5,
        input_keys=["input"],
    )

    system_prefix = """You are an agent designed to interact with a SQL database that contains information about investment funds offered by a bank.
    Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
    If the user doesn't specify the number of results, limit your query to at most 30 results.
    You can order the results by a relevant column to return the most interesting examples in the database.
    Never query for all the columns from a specific table, only ask for the relevant columns given the question.
    Always return a list of clients or nothing if no user satisfies the criteria.
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

    db = SQLDatabase.from_uri("sqlite:///data/dbfunds.db")
    model_name = os.getenv("MODEL_NAME")
    print(f"\nFunds Agent is using {model_name}")
    llm = ChatOpenAI(model=model_name,temperature=0)
    agent = create_sql_agent(
        llm=llm,
        db=db,
        prompt=full_prompt,
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
        #print(result["intermediate_steps"][0][0].log)

if __name__ == "__main__":
    main()