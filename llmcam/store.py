"""Module for constructing AppletStore."""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/10_store.ipynb.

# %% auto 0
__all__ = ['ToolBox', 'road_digitraffic', 'train_digitraffic', 'marine_digitraffic', 'load_oas', 'add_api_tools',
           'execute_function', 'add_function_tools', 'remove_service', 'clean_toolbox', 'save_toolbox', 'load_toolbox',
           'extract_tools_from_services', 'redirect_tool_calls']

# %% ../nbs/10_store.ipynb 3
import requests
import yaml
import json
import os

from .oas_to_requests import toolbox_schema
from typing import Optional

# %% ../nbs/10_store.ipynb 4
ToolBox = {}

# %% ../nbs/10_store.ipynb 6
def load_oas(
    oas_url: str = "https://tie.digitraffic.fi/swagger/openapi.json",  # OpenAPI Specification URL
    destination: str = "api/road_digitraffic.json",  # Destination file
    overwrite: bool = False  # Overwrite existing file
) -> dict:  # OpenAPI Specification
    """Load OpenAPI Specification from URL or file."""
    # Create destination directory if it does not exist
    os.makedirs(os.path.dirname(destination), exist_ok=True)

    # Download OpenAPI Specification if it does not exist or overwrite is True
    if not os.path.exists(destination) or overwrite:
        r = requests.get(oas_url)
        with open(destination, "w") as f:
            f.write(r.text)

    # Load OpenAPI Specification
    with open(destination, "r") as f:
        if destination.endswith(".json"):
            return json.load(f)
        elif destination.endswith(".yaml") or destination.endswith(".yml"):
            return yaml.load(f)
        else:
            raise ValueError("Invalid file format")

# %% ../nbs/10_store.ipynb 9
road_digitraffic = load_oas(
    oas_url="https://tie.digitraffic.fi/swagger/openapi.json",
    destination="api/road_digitraffic.json",
    overwrite=False
)
train_digitraffic = load_oas(
    oas_url="https://rata.digitraffic.fi/swagger/openapi.json",
    destination="api/train_digitraffic.json",
    overwrite=False
)
marine_digitraffic = load_oas(
    oas_url="https://meri.digitraffic.fi/swagger/openapi.json",
    destination="api/marine_digitraffic.json",
    overwrite=False
)

# %% ../nbs/10_store.ipynb 14
def add_api_tools(
    service_name: str,  # Name of the API service
    base_url: str,  # Base URL of the API service
    oas_url: Optional[str] = None,  # OpenAPI Specification URL
    oas_destination: Optional[str] = None # OpenAPI Specification destination file
):
    """Add API tools to the toolbox."""
    # Load OpenAPI Specification
    if oas_url is None:
        oas_url = f"{base_url}/swagger/openapi.json"
    if oas_destination is None:
        oas_destination = f"api/{service_name}.json"
    oas = load_oas(oas_url, oas_destination, overwrite=True)

    # Create tool schema and append to toolbox
    global ToolBox
    ToolBox[service_name] = toolbox_schema(base_url, oas)

# %% ../nbs/10_store.ipynb 18
from importlib import import_module
from typing import Callable, Any
from .fn_to_fc import tool_schema

# %% ../nbs/10_store.ipynb 23
def execute_function(
    function_name: str,  # Name of the function
    tools: list = [],  # The toolbox schema
    **kwargs  # Keyword arguments
) -> Any:  # Function output
    """Execute function with specified name."""
    # Get function from toolbox
    for tool in tools:
        if tool["function"]["name"] == function_name:
            module = tool["function"]["parameters"]["properties"]["module"]["default"]

    # Import module and get function
    if module is None:
        raise ValueError("Module not found")
    if module == "builtins":
        func: Callable = getattr(__builtins__, function_name, None)
    else:
        func: Callable = getattr(import_module(module), function_name, None)
    
    # Execute function
    if func is None:
        raise ValueError("Function not found")
    return func(**kwargs)

# %% ../nbs/10_store.ipynb 27
def add_function_tools(
    service_name: str,  # Name of the service
    function_names: list[str],  # List of function names (with module prefix)
):
    """Add function tools to the toolbox."""
    # Initialize tools
    tools = []

    # Import functions
    for function_name in function_names:
        # Get module prefix
        module_prefix = function_name.split(".")
        if len(module_prefix) == 1:
            module_prefix = "builtins"
        else:
            module_prefix = ".".join(module_prefix[:-1])

        # Get function name without module prefix
        func_name = function_name.split(".")[-1]

        # Import function
        if module_prefix == "builtins":
            func: Callable = getattr(__builtins__, func_name, None)
        else:
            func: Callable = getattr(import_module(module_prefix), func_name, None)

        # Raise error if function not found
        if func is None:
            raise ValueError(f"Function not found: {function_name}")
        
        # Create tool schema
        tools.append(tool_schema(func))

    # Append tools to toolbox
    global ToolBox
    for function_name in function_names:
        ToolBox[service_name] = tools

# %% ../nbs/10_store.ipynb 30
def remove_service(service_name: str):
    """Remove service from toolbox."""
    global ToolBox
    if service_name in ToolBox:
        del ToolBox[service_name]

#| export
def clean_toolbox():
    """Remove all services from toolbox."""
    global ToolBox
    ToolBox = {}

# %% ../nbs/10_store.ipynb 31
def save_toolbox(destination: str = "toolbox.json"):
    """Save toolbox to file."""
    with open(destination, "w") as f:
        json.dump(ToolBox, f)
    
#| export
def load_toolbox(destination: str = "toolbox.json"):
    """Load toolbox from file."""
    global ToolBox
    with open(destination, "r") as f:
        ToolBox = json.load(f)

# %% ../nbs/10_store.ipynb 32
def extract_tools_from_services(
    services: list[str] = []  # List of service names
) -> list:  # List of tools
    """Extract tools from services."""
    # Initialize tools
    tools = []

    # Extract tools from services
    global ToolBox
    for service in services:
        if service in ToolBox:
            tools.extend(ToolBox[service])

    # Raise error if no tools found
    if len(tools) == 0:
        raise ValueError("No tools found")
    
    # Raise error if too many tools
    if len(tools) > 128:
        raise ValueError("Too many tools for using GPT-4. Maximum number of tools is 128.")

    # Return tools
    return tools

# %% ../nbs/10_store.ipynb 35
add_api_tools(
    service_name="road_digitraffic",
    base_url="https://tie.digitraffic.fi",
    oas_url="https://tie.digitraffic.fi/swagger/openapi.json",
    oas_destination="api/road_digitraffic.json"
)

# %% ../nbs/10_store.ipynb 36
add_api_tools(
    service_name="train_digitraffic",
    base_url="https://rata.digitraffic.fi",
    oas_url="https://rata.digitraffic.fi/swagger/openapi.json",
    oas_destination="api/train_digitraffic.json"
)

# %% ../nbs/10_store.ipynb 38
add_function_tools(
    service_name="ytube_live",
    function_names=[
        "llmcam.fn_to_fc.capture_youtube_live_frame_and_save",
        "llmcam.fn_to_fc.ask_gpt4v_about_image_file"
    ]
)

# %% ../nbs/10_store.ipynb 40
from .oas_to_requests import generate_request

def redirect_tool_calls(
    function_name: str,  # Name of the function
    tools: list = [],  # List of tools
    **kwargs  # Keyword arguments
):
    """Redirect tool calls to the appropriate function."""
    for tool in tools:
        if tool["function"]["name"] == function_name:
            if "module" in tool["function"]["parameters"]["properties"]:
                return execute_function(
                    function_name=function_name, 
                    tools=tools, 
                    **kwargs)
            
            elif "url" in tool["function"]["parameters"]["properties"]:
                return generate_request(
                    function_name=function_name, 
                    tools=tools, 
                    **kwargs)
    
    raise ValueError("Function not found")