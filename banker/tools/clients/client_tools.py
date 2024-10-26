from langchain.agents import tool
from typing import List
import random
import re
import sqlite3
from collections import Counter
from sklearn.metrics import jaccard_score
import numpy as np

def get_client_info(conn, dni):
    """Fetch client information by their DNI, including net worth."""
    cursor = conn.cursor()
    cursor.execute("SELECT dni, name, surname, birth_year, net_worth, preferences FROM clients WHERE dni = ?", (dni,))
    return cursor.fetchone()

def get_client_investments(conn, dni):
    """Fetch the list of ISINs in which the client has invested."""
    cursor = conn.cursor()
    cursor.execute("SELECT isin FROM investments WHERE dni = ?", (dni,))
    return [row[0] for row in cursor.fetchall()]

def get_all_clients(conn):
    """Fetch information for all clients."""
    cursor = conn.cursor()
    cursor.execute("SELECT dni, name, surname, birth_year, net_worth, preferences FROM clients")
    return cursor.fetchall()

def jaccard_similarity(list1, list2):
    """Calculate Jaccard similarity between two lists of preferences."""
    set1, set2 = set(list1.split()), set(list2.split())
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

def similarity_score(client1, client2, inv1, inv2):
    """Calculate a similarity score between two clients."""
    # Normalized age difference
    age_diff = abs(client1[3] - client2[3])
    age_score = 1 / (1 + age_diff)
    
    # Preference similarity using Jaccard
    pref_score = jaccard_similarity(client1[5], client2[5])
    
    # Investment similarity: proportion of common funds
    common_funds = len(set(inv1).intersection(set(inv2)))
    total_funds = len(set(inv1).union(set(inv2)))
    inv_score = common_funds / total_funds if total_funds != 0 else 0
    
    # Normalized net worth difference
    net_worth_diff = abs(client1[4] - client2[4])
    max_net_worth = max(client1[4], client2[4], 1)  # Avoid division by 0
    net_worth_score = 1 - (net_worth_diff / max_net_worth)
    
    # Weighting: adjust the weight of each factor based on importance
    return 0.3 * age_score + 0.2 * pref_score + 0.3 * inv_score + 0.2 * net_worth_score

def find_similar_clients(conn, dni, N=5):
    """Find N similar clients, returnin a lista of DNIs."""
    target_client = get_client_info(conn, dni)
    target_investments = get_client_investments(conn, dni)
    
    all_clients = get_all_clients(conn)
    similarities = []
    
    for client in all_clients:
        if client[0] != dni:
            investments = get_client_investments(conn, client[0])
            score = similarity_score(target_client, client, target_investments, investments)
            similarities.append((client[0], score))  # Guardar DNI y puntaje de similitud
    
    # Ordenar por puntaje de similitud en orden descendente
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Retornar solo los DNIs de los N clientes más similares
    return [dni for dni, score in similarities[:N]]


@tool
def get_similar_clients(client_id:str) -> List[str]:
    """Use this tool to know which clients are similar to the client passed as parameter. The tool
    returns a list with the DNIs of similar clients"""

    # Check if format is DNI
    dni_pattern = r'^\d{8}[A-HJ-NP-TV-Z]$'
    
    if re.match(dni_pattern, client_id):
        conn = sqlite3.connect('data/dbclients.db')
        similars = find_similar_clients(conn, client_id, N=3)
        conn.close()
        return similars
    else:
        return "Error: this tool expects a dni code that represents a user"
    
    
@tool 
def get_client_benefits(input_data) -> float:
    """ Use this tool to calculate the benefits or losses of a client during certain period of time. 
    Use this tool with one parameter that is a dictionary like
      "{"client_id": "string", "days": int}" when you need to retrieve benefits"""
    benefits = round(random.uniform(-10, 10), 1)
    print(f"Los beneficios son {benefits}")
    return float(benefits)