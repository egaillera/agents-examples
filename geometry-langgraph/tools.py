from langchain_core.tools import tool
import random
import json


@tool
def get_circle_area(radius:float) -> float:
    """ Returns the area of a circle. Input is a number with the value of the radius"""
    radius_number = float(radius)
    return float(3.1416*radius_number*radius_number)

@tool
def get_square_area(edge:float) -> float:
    """Returns the area of a square. Input is a number with the value of the edge"""
    edge_number = float(edge)
    return float(edge_number*edge_number)

