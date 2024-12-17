"""Automatically generate OAS from python class implementation via OpenAI API"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/core/04_class_to_oas.ipynb.

# %% auto 0
__all__ = ['api', 'content']

# %% ../../nbs/core/04_class_to_oas.ipynb 3
import json
from openai import OpenAI
import yaml
from openapi_spec_validator import validate_spec

# %% ../../nbs/core/04_class_to_oas.ipynb 6
#| eval: false
api = OpenAI()

# %% ../../nbs/core/04_class_to_oas.ipynb 7
content = """
Given the following Python class, generate an OpenAPI 3.0 specification that defines endpoints
for creating, updating, and retrieving instances of the class. Also, define the schema for the class in OpenAPI.
Please return OpenAPI 3.0 specification yaml file only.

Python Class:
class Item:
    def __init__(self, name: str, price: float, quantity: int):
        self.name = name
        self.price = price
        self.quantity = quantity

    def get_total_price(self) -> float:
        return self.price * self.quantity
        """
