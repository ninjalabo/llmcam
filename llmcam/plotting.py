"""plot json data and download an plotted image"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/14_plotting.ipynb.

# %% auto 0
__all__ = ['plot_object']

# %% ../nbs/14_plotting.ipynb 3
from .file_manager import list_image_files
from .gpt4v import ask_gpt4v
from .yolo import detect_objects
from .fn_to_fc import tool_schema, complete, form_msgs, print_msgs
import os
import json
import matplotlib.pyplot as plt

# %% ../nbs/14_plotting.ipynb 4
def plot_object(
        images: list[str], # list of images to be extracted
        object: str, # object to detect
        path: str = "object_count_bar_plot.png", # path to save plot
        yolo: bool = False # whether to use YOLO or GPT only
        ):
  """Plot the number of object specified through multiple images, accept singular form for object only."""
  count = []
  if yolo:
    for image in images:
      image = image.split("/")[-1]
      info = json.loads(detect_objects(os.getenv("LLMCAM_DATA", "../data") + "/" + image))
      count.append(info.get(object, 0))
  else:
    for image in images:
      image = image.split("/")[-1]
      info = ask_gpt4v(os.getenv("LLMCAM_DATA", "../data") + "/" + image)
      count.append(info.get(object, 0))
      
  plt.figure(figsize=(10, 6))
  plt.bar(images, count, color='skyblue')
  plt.title(f'Number of {object} Detected per Image')
  plt.xlabel('Image')
  plt.ylabel(f'Number of {object}')
  plt.xticks(range(len(images)), [f"Image {i+1}" for i in range(len(images))], rotation=45)
  plt.grid(axis='y', linestyle='--', alpha=0.7)
  
  plt.savefig(path)
  plt.close()
    
  return path