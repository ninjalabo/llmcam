"""python module to convert a given Class into FC automatically"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/06_class_to_fc.ipynb.

# %% auto 0
__all__ = ['tool_schema', 'fn_name', 'fn_args', 'fn_exec', 'fn_result_content', 'complete']

# %% ../nbs/06_class_to_fc.ipynb 3
import openai
import json
import inspect
from typing import Optional

# %% ../nbs/06_class_to_fc.ipynb 7
def tool_schema(func):
    """ automatically generate a schema from its parameters and docstring"""
    # Extract function name, docstring, and parameters
    func_name = func.__name__
    func_description = func.__doc__ or "No description provided."
    signature = inspect.signature(func)
    
    # Create parameters schema
    parameters_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    # Populate properties and required fields
    for param_name, param in signature.parameters.items():
        param_type = param.annotation if param.annotation != inspect._empty else str
        # Map Python types to JSON Schema types
        json_type = "string" if param_type == str else "number" if param_type in [int, float] else "boolean"
        
        # Add parameter to schema
        parameters_schema["properties"][param_name] = {
            "type": json_type,
            "description": f"{param_name} parameter of type {param_type.__name__}"
        }
        
        # Mark as required if no default
        if param.default == inspect.Parameter.empty:
            parameters_schema["required"].append(param_name)
    
    # Build final tool schema
    tool_schema = [
        {
            "type": "function",
            "function": {
                "name": func_name,
                "description": func_description,
                "parameters": parameters_schema,
            }
        }
    ]
    return tool_schema

# %% ../nbs/06_class_to_fc.ipynb 9
# Support functions to handle tool response,where res == response.choices[0].message
def fn_name(res): return res.tool_calls[0].function.name
def fn_args(res): return json.loads(res.tool_calls[0].function.arguments)    
def fn_exec(res): return globals().get(fn_name(res))(**fn_args(res))
def fn_result_content(res):
    """Create a content containing the result of the function call"""
    content = dict()
    content.update(fn_args(res))
    content.update({fn_name(res): fn_exec(res)})
    return json.dumps(content)

# %% ../nbs/06_class_to_fc.ipynb 10
def complete(role, content, tool_call_id=None):
    "Send completion request with messages, and save the response in messages again"
    messages.append({"role":role, "content":content, "tool_call_id":tool_call_id})
    response = openai.chat.completions.create(model="gpt-4o", messages=messages, tools=tools)
    res = response.choices[0].message
    messages.append(res.to_dict())
    if res.to_dict().get('tool_calls'):
        complete(role="tool", content=fn_result_content(res), tool_call_id=res.tool_calls[0].id)
    return messages[-1]['role'], messages[-1]['content']