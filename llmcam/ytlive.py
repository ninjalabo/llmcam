"""This module is used to capture images from YouTube live."""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_ytlive.ipynb.

# %% auto 0
__all__ = ['nakyma_helsinki_known_places', 'nakyma_helsinkigista_youtube_live_url', 'ydl_opts', 'stream_url', 'show_frame',
           'crop_frame', 'frame_to_text', 'known', 'meta', 'fname', 'YTLive', 'NHsta']

# %% ../nbs/01_ytlive.ipynb 3
from datetime import datetime
from IPython.display import Image, display
from matplotlib import pyplot as plt
from pathlib import Path
from PIL import Image
import cv2
import glob
import matplotlib.pyplot as plt
import os
import pytesseract
import time
import yt_dlp as youtube_dl

# %% ../nbs/01_ytlive.ipynb 5
nakyma_helsinki_known_places = [
    "Olympiaterminaali",
    "Etelasatama",
    #"Eteläsatama",  # fixup
    "Eteladsatama", # fixup
    "Presidentinlinna",
    "Tuomiokirkko",
    "Kauppatori",
    "Kauppator",    # fixup   
    "Torni",
    "Valkosaari",
]

# %% ../nbs/01_ytlive.ipynb 7
nakyma_helsinkigista_youtube_live_url = "https://www.youtube.com/watch?v=LMZQ7eFhm58"
ydl_opts = {
    'cookiefile': "cookies.txt",  # Path to the exported cookies file,  # Use cookies for authentication
    'download': False  # Set to True if you want to download
}

# %% ../nbs/01_ytlive.ipynb 9
def stream_url(ytlive_url:str, ydl_opts:dict) -> str:
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(ytlive_url, download=False)
        for o in info['formats']:
            if o['resolution'] == '1280x720':
                return o['url']
        else:
            raise ValueError("No 1280x720 format")    

# %% ../nbs/01_ytlive.ipynb 10
def show_frame(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Convert from BGR to RGB for Matplotlib
    plt.imshow(frame_rgb)
    plt.axis('off')  # Hide axes
    plt.show()   

# %% ../nbs/01_ytlive.ipynb 11
def crop_frame(frame, crop=(0, 0, 480, 30)):
    x, y, w, h = crop
    return frame[y:y+h, x:x+w]    

# %% ../nbs/01_ytlive.ipynb 12
def frame_to_text(frame): return pytesseract.image_to_string(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).strip()

# %% ../nbs/01_ytlive.ipynb 13
def known(txt:str, known_places:str) -> str:
    "try to find one of `known_places` are included in the given `txt`"
    for o in known_places:
        #print(o, "in", txt)
        if o in txt:
            return o
    raise Exception("No place specified")

# %% ../nbs/01_ytlive.ipynb 15
def meta(frame, known_places=nakyma_helsinki_known_places, printing=False):
    "Withdraw meta data, datetime & place"
    # "04.10.2024  14:53:49  Kauppatori", Original format
    txt = frame_to_text(frame)
    if printing==True: print(txt)
    dt = datetime.strptime(txt[:19],"%d.%m.%Y %H:%M:%S")
    pl = known(txt[20:], known_places)
    pl = pl.replace("Eteladsatama", "Etelasatama") # fixup
    pl = pl.replace("ä", "a")                      # fixup
    pl = pl.replace("kauppator", "kauppatori")     # fixup
    return dt, pl

# %% ../nbs/01_ytlive.ipynb 16
def fname(prefix, dt, pl): return f"""{prefix}{dt.strftime("%Y.%m.%d_%H:%M:%S")}_{pl}.jpg"""

# %% ../nbs/01_ytlive.ipynb 19
class YTLive:
    def __init__(self,
                 url:str, # YouTube Live URL
                 data_dir:Path = Path(os.getenv("LLMCAM_DATA", "../data")), # directory to store captured images
                 place:str="nowhere", # place name
                ):
        self.url = url
        self.stream_url = stream_url(url, ydl_opts)
        self.data_dir = data_dir
        self.place = place

    def file_name(self, frame=None):
        return fname("cap_", datetime.now(), self.place)

    def capture(self) -> Path:
        cap = cv2.VideoCapture(self.stream_url)
        ret, frame = cap.read()
        if ret==False:
            raise Exception("Failed to capture frame.")
        fn = self.data_dir/self.file_name(frame)
        cv2.imwrite(fn, frame)
        return fn     

    def __call__(self):
        # __call__ method allows the instance to be called like a function
        return self.capture()

# %% ../nbs/01_ytlive.ipynb 22
class NHsta(YTLive):
    def __init__(self,
                 url:str="https://www.youtube.com/watch?v=LMZQ7eFhm58", # YouTube Live URL
                 data_dir:Path = Path(os.getenv("LLMCAM_DATA", "../data")), # directory to store captured images
                 place:str="unclear", # place name if OCR doesn't work
                ):
        super().__init__(url, data_dir, place)
    
    def file_name(self, frame):
        try:        
            path = fname("cap_", *meta(crop_frame(frame), printing=True))
        except Exception as e:
            path = super().file_name()
            print(path)
        return path
