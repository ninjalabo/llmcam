# Function to Tool Schema


<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

To execute function calling from GPT responses, we need to define the
function and its schema as a GPT tool. However, it can be inconvenient
to define both, especially if we need to incorporate multiple functions
as GPT tools.

This process can be simplified if we utilize type-hinting and
annotations on functions supported by Python using libraries such as
`inspect` and `ast`. Summary of our schema generation process:

    <div style="display: flex; justify-content: center; align-items: center; width: 100%; height: 100%;">
        <img src="https://mermaid.ink/img/CmZsb3djaGFydCBURAogICAgRltGdW5jdGlvbl0gLS0-fGFzdHwgUERbUGFyYW10ZXIgZGVzY3JpcHRpb25zXQogICAgRiAtLT58aW5zcGVjdHwgUFRbUGFyYW1ldGVyIHR5cGVzXQogICAgUFQgLS0-IENQVFtHUFQtY29tcGF0aWJsZSBwYXJhbWV0ZXIgdHlwZXNdCiAgICBGIC0tPnxiYXNpYyBwcm9wZXJ0aWVzfCBNZXRhZGF0YQogICAgTWV0YWRhdGEgLS0-IFNbU2NoZW1hXQogICAgQ1BUIC0tPiBTCiAgICBQRCAtLT4gUwogICAgRUB7IHNoYXBlOiBicmFjZXMsIGxhYmVsOiAiRml4dXAgZnVuY3Rpb24gClNlcnZpY2UgbmFtZSAKRXh0cmEgbWV0YWRhdGEiIH0KICAgIEUgLS0-IFMK" style="max-width: 100%; max-height: 100%; object-fit: contain;" />
    </div>
    &#10;

Let us start with a well-documented function `get_weather_information`:

``` python
# Define the function to get weather information
from typing import Optional

def get_weather_information(
    city: str,  # Name of the city
    zip_code: Optional[str] = None,  # Zip code of the city (optional)
):
    """Get weather information for a city or location based on zip code"""
    return {
        "city": city,
        "zip_code": zip_code,
        "temparature": 25,
        "humidity": 80,
    }
```

------------------------------------------------------------------------

### get_weather_information

>  get_weather_information (city:str, zip_code:Optional[str]=None)

*Get weather information for a city or location based on zip code*

<table>
<thead>
<tr>
<th></th>
<th><strong>Type</strong></th>
<th><strong>Default</strong></th>
<th><strong>Details</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td>city</td>
<td>str</td>
<td></td>
<td>Name of the city</td>
</tr>
<tr>
<td>zip_code</td>
<td>Optional</td>
<td>None</td>
<td>Zip code of the city (optional)</td>
</tr>
</tbody>
</table>

The function is well-documented and its annotations contain almost all
necessary information for tool schema. We will build utilities around
extracting such information and converting them into appropriate formats
for tool schema.

## Parameter descriptions

We can extract the descriptions of function parameters with the `ast`
library. In our implementation, we can follow the inline comments for
conveniency. The descriptions can be extracted as follows:

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/core/fn_to_schema.py#L17"
target="_blank" style="float:right; font-size:smaller">source</a>

### extract_parameter_comments

>  extract_parameter_comments (func:Callable)

*Extract comments for function arguments*

<table>
<thead>
<tr>
<th></th>
<th><strong>Type</strong></th>
<th><strong>Details</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td>func</td>
<td>Callable</td>
<td>Function to extract comments from</td>
</tr>
<tr>
<td><strong>Returns</strong></td>
<td><strong>dict</strong></td>
<td><strong>Dictionary with parameter comments</strong></td>
</tr>
</tbody>
</table>

Example of extracting comments from the function:

``` python
extract_parameter_comments(get_weather_information)
```

    {'city': 'Name of the city', 'zip_code': 'Zip code of the city (optional)'}

## Type converter

Python types cannot be directly transferred into acceptable data types
in GPT-compatible tool schema. Therefore, we need an utility to convert
these types:

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/core/fn_to_schema.py#L44"
target="_blank" style="float:right; font-size:smaller">source</a>

### param_converter

>  param_converter (param_type, description)

*Convert Python parameter types to acceptable types for tool schema*

<table>
<thead>
<tr>
<th></th>
<th><strong>Type</strong></th>
<th><strong>Details</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td>param_type</td>
<td></td>
<td>The type of the parameter</td>
</tr>
<tr>
<td>description</td>
<td></td>
<td>The description of the parameter</td>
</tr>
<tr>
<td><strong>Returns</strong></td>
<td><strong>dict</strong></td>
<td><strong>The converted parameter</strong></td>
</tr>
</tbody>
</table>

Test with parameters of `get_weather_information`:

``` python
city_param = param_converter(str, "Name of the city")
zip_param = param_converter(Optional[str], "Zip code of the city (optional)")
city_param, zip_param
```

    ({'type': 'string', 'description': 'Name of the city'},
     {'anyOf': [{'type': 'string',
        'description': 'Zip code of the city (optional)'},
       {'type': 'null',
        'description': 'A default value will be automatically used.'}]})

## Function to Schema

We can combine the above utilities with other utilities in `inspect` to
extract information from a Python function and generate a tool schema.

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/core/fn_to_schema.py#L89"
target="_blank" style="float:right; font-size:smaller">source</a>

### function_schema

>  function_schema (func:Callable, service_name:Optional[str]=None,
>                       fixup:Optional[Callable]=None, **kwargs)

*Generate a schema from function using its parameters and docstring*

<table>
<thead>
<tr>
<th></th>
<th><strong>Type</strong></th>
<th><strong>Default</strong></th>
<th><strong>Details</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td>func</td>
<td>Callable</td>
<td></td>
<td>The function to generate the schema for</td>
</tr>
<tr>
<td>service_name</td>
<td>Optional</td>
<td>None</td>
<td>The name of the service</td>
</tr>
<tr>
<td>fixup</td>
<td>Optional</td>
<td>None</td>
<td>A function to fix up the schema</td>
</tr>
<tr>
<td>kwargs</td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td><strong>Returns</strong></td>
<td><strong>dict</strong></td>
<td></td>
<td><strong>The generated tool schema</strong></td>
</tr>
</tbody>
</table>

Test with our current function:

``` python
tool_schema = function_schema(get_weather_information, service_name="Weather Service")
tool_schema
```

    {'type': 'function',
     'function': {'name': 'get_weather_information',
      'description': 'Get weather information for a city or location based on zip code',
      'parameters': {'type': 'object',
       'properties': {'city': {'type': 'string',
         'description': 'Name of the city'},
        'zip_code': {'anyOf': [{'type': 'string',
           'description': 'Zip code of the city (optional)'},
          {'type': 'null',
           'description': 'A default value will be automatically used.'}]}},
       'required': ['city']},
      'metadata': {'module': '__main__', 'service': 'Weather Service'}}}

## Simulated GPT workflow

Test integrating with our current GPT framework:

``` python
from llmcam.core.fc import *

tools = [function_schema(get_weather_information, service_name="Weather Service")]
messages = form_msgs([
    ("system", "You can get weather information for a given location using the `get_weather_information` function"),
    ("user", "What is the weather in New York?")
])
complete(messages, tools=tools)
print_msgs(messages)
```

    >> System:
    You can get weather information for a given location using the `get_weather_information` function
    >> User:
    What is the weather in New York?
    >> Assistant:
    The current weather in New York is 25°C with 80% humidity.