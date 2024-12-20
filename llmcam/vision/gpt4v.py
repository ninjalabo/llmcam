"""Python module for processing image by asking GPT via OpenAI API"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/vision/02_gpt4v.ipynb.

# %% auto 0
__all__ = ['question', 'encode_image', 'info', 'ask_gpt4v_about_image_file']

# %% ../../nbs/vision/02_gpt4v.ipynb 3
from IPython.display import Image
import base64
import glob
import json
import openai
import requests

# %% ../../nbs/vision/02_gpt4v.ipynb 7
def encode_image(fname: str):
    """Encode an image file as base64 string"""
    with open(fname, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

# %% ../../nbs/vision/02_gpt4v.ipynb 12
question = """
    Describe this image quantitatively as many as possible in json format. All the value should numbers.
    
    ##### EXAMPLE OUTPUT FORMAT
    {
        'timestamp': '2024-10-06T19:04:14',
        'location': 'Kauppatori',
        'dimensions': '1280 x 720',
        'building': 10,
        'buildings_height_range': '3-5 stories',
        'car': 5,
        'truck': 2,
        'boat': 4,
        'available_parking_space': 3,
        'street_lights': 20,
        'person': 10,
        'time_of_day': 'evening',
        'artificial_lighting': 'prominent',
        'visibility_clear': True,
        'sky_visible': True,
        'sky_light_conditions': 'dusk',
        'waterbodies_visible': True,
        'waterbodies_type': 'harbor'
    }
    """

# %% ../../nbs/vision/02_gpt4v.ipynb 15
def info(response):
    txt = json.loads(response.json())['choices'][0]['message']['content']
    data = json.loads(txt.replace('```json\n', "").replace('\n```', ""))
    return data

# %% ../../nbs/vision/02_gpt4v.ipynb 18
def ask_gpt4v_about_image_file(
        path:str  # Path to the image file
    ) -> str:  # JSON string with quantitative information
    """Tell all about quantitative information from a given image file"""
    response = openai.chat.completions.create(
      model="gpt-4o",
      messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": question,},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encode_image(path)}", "detail":"high",},
                },
            ],
        }],
      max_tokens=300,
    )
    return info(response)