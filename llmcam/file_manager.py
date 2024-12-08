"""retrieve files with time & location specified"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/13_fle_manager.ipynb.

# %% auto 0
__all__ = ['list_image_files', 'list_detection_files', 'list_demo3_files', 'list_plot_files']

# %% ../nbs/13_fle_manager.ipynb 3
import os
import glob

# %% ../nbs/13_fle_manager.ipynb 7
def list_image_files()->str:
    """List all captured image files.
    file naming scheme is "cap_%Y.%m.%d_%H:%M:%S_<place name>.jpg"
    """
    return "\n".join(glob.glob(os.getenv("LLMCAM_DATA", "../data")+"/"+"cap_*.jpg"))

# %% ../nbs/13_fle_manager.ipynb 8
def list_detection_files() -> str:
  """List all detection images. File name starts with detection_"""
  return "\n".join(glob.glob(os.getenv("LLMCAM_DATA", "../data")+ "/" + "detection_*.jpg"))

# %% ../nbs/13_fle_manager.ipynb 9
def list_demo3_files() -> str:
  """List all parking lot frames. File name starts with demo3_"""
  return "\n".join(glob.glob(os.getenv("LLMCAM_DATA", "../data")+ "/" + "demo3_*.jpg"))

# %% ../nbs/13_fle_manager.ipynb 10
def list_plot_files() -> str:
  """List all plots. File name ends with plot"""
  return "\n".join(glob.glob(os.getenv("LLMCAM_DATA", "../data")+ "/" + "*plot.jpg"))
