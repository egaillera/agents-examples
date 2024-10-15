from langchain.agents import tool
from typing import List
import random
import re

@tool
def get_similar_clients(client_id:str) -> List[str]:
    """ Use this tool to know which clients are similar to the client passed as parameter. Tool
    return a list with the id of the similar clients"""

    # Check if format is DNI
    dni_pattern = r'^\d{8}[A-HJ-NP-TV-Z]$'
    
    if re.match(dni_pattern, client_id):
        return ["20409152X","60044831L"]
    else:
        return "Error: this tool expects a code that represents a user"
    
    
@tool 
def get_client_benefits(input_data) -> float:
    """ Use this tool to calculate the benefits or losses of a client during certain period of time. 
    Use this tool with one parameter that is a dictionary like
      "{"client_id": "string", "days": int}" when you need to retrieve benefits"""
    benefits = round(random.uniform(-10, 10), 1)
    print(f"Los beneficios son {benefits}")
    return float(benefits)