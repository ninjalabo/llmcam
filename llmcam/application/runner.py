"""Python module for running Chat UI Application from a general Python script."""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/application/03_runner.ipynb.

# %% auto 0
__all__ = ['run_llmcam']

# %% ../../nbs/application/03_runner.ipynb 4
import asyncio
import os
import uvicorn
from fastcore.parallel import startthread

# %% ../../nbs/application/03_runner.ipynb 6
def run_llmcam(
    host="0.0.0.0",  # The host to listen on
    port=5001,  # The port to listen on
    data_path=None,  # The path to the data directory
    openai_key=None,  # The OpenAI API key
):
    """Run the LLMCAM chatbot application"""
    # Import app from chat_ui base module
    from llmcam.application.chat_ui import app

    # Set the data path and OpenAI key
    if data_path is not None: os.environ["LLMCAM_DATA"] = data_path
    if openai_key is not None: os.environ["OPENAI_API_KEY"] = openai_key
    
    # Run the server with uvicorn
    server = uvicorn.Server(uvicorn.Config(app, host=host, port=port))
    async def async_run_server(server): await server.serve()
    asyncio.run(async_run_server(server))
