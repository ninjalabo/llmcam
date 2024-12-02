"""chat UI implemented in fastHTML"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/05_chat_ui.ipynb.

# %% auto 0
__all__ = ['session_messages', 'session_tools', 'default_tools', 'hdrs', 'app', 'scroll_script', 'title_script',
           'prepare_handler_schemas', 'execute_handler', 'init_session', 'ChatMessage', 'ChatInput', 'ActionButton',
           'ActionPanel', 'ToolPanel', 'index', 'chat_disconnect', 'wschat', 'get_file', 'llmcam_chatbot']

# %% ../nbs/05_chat_ui.ipynb 4
import uvicorn
import uuid
import os
from fasthtml.common import *
from fastcore.parallel import startthread
from typing import Callable, Optional

from .fn_to_fc import capture_youtube_live_frame_and_save, ask_gpt4v_about_image_file
from .fn_to_fc import tool_schema, complete, form_msg
from .store import add_api_tools, add_function_tools, remove_tools
from .store import execute_handler_core, handler_schema
from .yolo import detect_objects
from .dtcam import *
from .file_manager import list_image_files, list_detection_files
from .plotting import plot_object
from .bash_command import *

# %% ../nbs/05_chat_ui.ipynb 5
# Set up database for information per session
session_messages = {}
session_tools = {}

# %% ../nbs/05_chat_ui.ipynb 6
# Set up default tools
default_tools = [tool_schema(fn) for fn in (
    capture_youtube_live_frame_and_save, 
    ask_gpt4v_about_image_file,
    detect_objects,
    cap,
    list_image_files,
    list_detection_files,
    plot_object,
    execute_bash_command,
    camera_address_book,
)]

# %% ../nbs/05_chat_ui.ipynb 7
# Utility functions to manage tools per session
def prepare_handler_schemas(
    session_id: str,  # Session ID to use
    fixup: Callable = None,  # Optional function to fix up the execution
):
    return [
        handler_schema(function, service_name="toolbox_manager", fixup=fixup, session_id=session_id) for \
        function in [add_api_tools, add_function_tools, remove_tools]
    ]

def execute_handler(
    function_name: str,  # Name of the function to execute
    session_id: str,  # Session ID to use
    **kwargs,  # Additional arguments to pass to the function
):
    tools = session_tools[session_id]
    return execute_handler_core(tools, function_name, **kwargs)

# %% ../nbs/05_chat_ui.ipynb 8
def init_session(session_id: Optional[str] = None):
    if session_id is None or session_id not in session_messages:
        # Initialize tools in session tools and create a session ID
        session_id = str(uuid.uuid4())

        # Add default tools and prepare handler schemas
        session_tools[session_id] = []
        session_tools[session_id].extend(default_tools)
        session_tools[session_id].extend(prepare_handler_schemas(session_id, execute_handler))

        # Initialize messages in session messages
        session_messages[session_id] = []
    
    return session_id

# %% ../nbs/05_chat_ui.ipynb 9
# Set up the app, including daisyui and tailwind for the chat component
hdrs = (picolink,
        Link(rel="icon", href=f"""{os.getenv("LLMCAM_DATA", "../data").split("/")[-1]}/favicon.ico""", type="image/png"),
        Script(src="https://cdn.tailwindcss.com"),
        Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css"),
        MarkdownJS(), HighlightJS(langs=['python', 'javascript', 'html', 'css']))
app = FastHTML(hdrs=hdrs, exts="ws")

# %% ../nbs/05_chat_ui.ipynb 11
# Chat message component (renders a chat bubble)
def ChatMessage(
        msg: str,  # Message to display
        user: bool  # Whether the message is from the user or assistant
    ):  # Returns a Div containing the chat bubble
    # Set class to change displayed style of bubble
    content_class = "chat-bubble chat-bubble-primary" if user else ""
    content_class += " marked py-2"
    return  Div(cls=f"chat chat-end py-4" if user else "py-4")(
                Div('User' if user else 'Assistant', cls="chat-header"),
                Div(
                    msg,
                    cls=content_class,
                )
            )

# %% ../nbs/05_chat_ui.ipynb 14
# The input field for the user message. Also used to clear the
# input field after sending a message via an OOB swap
def ChatInput():  # Returns an input field for the user message
    return Input(name='msg', id='msg-input', placeholder="Type a message",
                 cls="input input-bordered w-full rounded-l-2xl", 
                 hx_swap_oob='true'  # Re-render the element to remove submitted message
                )

# %% ../nbs/05_chat_ui.ipynb 17
def ActionButton(
        session_id: str,  # Session ID to use
        content: str,  # Text to display on the button
        message: str = None  # Message to send when the button is clicked
    ):  # Returns a button with the given content

    return Form(
        ws_send=True,
        hx_ext='ws', ws_connect='/wschat',
    )(
        Hidden(session_id, name="session_id"),
        Hidden(content if message is None else message, name="msg"),
        Button(
            content, 
            cls="btn btn-secondary rounded-2 h-fit", 
        )
    )

def ActionPanel(
        session_id: str  # Session ID to use
    ):  # Returns a panel of action buttons
    return Div(
        P("Quick actions", cls="text-lg text-black"),
        ActionButton(session_id, "Introduce your model GPT-4o"),
        ActionButton(session_id,
            "Extract information from a YouTube Live", 
            "Capture and extract information from a YouTube Live. Use the default link."),
        cls="flex flex-col h-fit gap-4 py-4 px-4"
    )

def ToolPanel(
        session_id: str  # Session ID to use
    ):  # Returns a panel of usable tools

    available_services = session_tools.get(session_id, [])

    # Generate list items for each available tool
    items = []
    if available_services:
        for service in available_services:
            service_desc = service['function']['description']
            items.append(Li(f"{service_desc}", cls="text-sm text-black"))
    else:
        items.append(Li("No services available", cls="text-sm italic text-gray-500"))

    return Div(
        P("Available Tools", cls="text-lg text-black"),
        Ul(*items, cls="list-disc list-inside px-6", style="max-height: 800px; overflow-y:auto;"),
        id="toollist",
        cls="flex flex-col h-fit gap-4 py-4 px-4"
    )

# %% ../nbs/05_chat_ui.ipynb 22
scroll_script = Script("""
  // Function to scroll to the bottom of an element
  function scrollToBottom(element) {
    element.scrollTop = element.scrollHeight;
  }

  // Reference the expanding element
  const expandingElement = document.getElementById('chatlist');

  // Observe changes to the element's content and scroll down automatically
  const observer = new MutationObserver(() => {
    scrollToBottom(expandingElement);
  });

  // Start observing the expanding element for changes
  observer.observe(expandingElement, { childList: true, subtree: true });
""")

# %% ../nbs/05_chat_ui.ipynb 23
title_script = Script("""
    // Function to set the title of the page
    document.title = "LLMCAM";
""")

# %% ../nbs/05_chat_ui.ipynb 24
@app.get('/')
async def index(session):
    # Initialize the session
    session_id = init_session(session_id=session.get('session_id'))
    
    # Set up the chat UI
    sidebar = Div(
        ActionPanel(session_id=session_id),
        ToolPanel(session_id=session_id),
        cls="w-[50vw] flex flex-col p-0",
        style="background-color: WhiteSmoke;"
    )
    page =  Div(cls="w-full flex flex-col p-0")(  # Main page
        Form(
            ws_send=True,
            hx_ext='ws', ws_connect='/wschat',
            cls="w-full flex flex-col px-24 h-[100vh]"
        )(
            Hidden(session_id, name="session_id"),
            # The chat list
            Div(id="chatlist", cls="chat-box overflow-y-auto flex-1 w-full mt-10 p-4")(
                # One initial message from AI assistant
                ChatMessage("Hello! I'm a chatbot. How can I help you today?", False),
            ),
            # Input form
            Div(cls="h-fit mb-5 mt-5 flex space-x-2 mt-2 p-4")(
                Group(
                    ChatInput(), 
                    Button("Send", cls="btn btn-primary rounded-r-2xl"))
            ),
            scroll_script,
            title_script
        )   
    )
    return Main(
        sidebar,
        page, 
        title="Chatbot",
        data_theme="wireframe",
        cls="h-[100vh] w-full relative flex flex-row items-stretch overflow-hidden transition-colors z-0 p-0",)

# %% ../nbs/05_chat_ui.ipynb 26
# On websocket disconnect, remove the session ID from the session messages and tools
def chat_disconnect(ws):
    """Remove session ID from session messages and tools on websocket disconnect"""
    session_id = ws.scope.get("session_id")
    if session_id in session_messages:
        del session_messages[session_id]
    if session_id in session_tools:
        del session_tools[session_id]

# %% ../nbs/05_chat_ui.ipynb 27
# The chatbot websocket handler
@app.ws('/wschat', disconn=chat_disconnect)
async def wschat(ws, msg: str, send, session_id: str):
    # Initialize the session
    session_id = init_session(session_id=session_id)

    # Set the session ID in the websocket scope
    ws.scope["session_id"] = session_id

    # Set up the global variables
    global session_tools
    global execute_handler
    
    # Create chat messages from the provided contents and roles
    messages = session_messages.get(session_id, [])
    if len(messages) == 0:
        messages.append(
            form_msg(
                "system", 
"You are a helpful assistant. Use the supplied tools to assist the user. \
If asked to show or display an image or plot, do it by embedding its path starting with \
`../data/<filename>` in Markdown syntax."
            ))
    messages.append(form_msg("user", msg))
    await send(
        Div(ChatMessage(
            messages[-1]["content"],
            messages[-1]["role"] == "user"), 
        hx_swap_oob='beforeend', id="chatlist"))
    
    await send(ChatInput())  # Clear the input field
    
    # Add the user's message to the chat history
    complete(messages, session_tools[session_id])
    await send(Div(ChatMessage(
            messages[-1]["content"],
            messages[-1]["role"] == "user"), hx_swap_oob='beforeend', id="chatlist"))
    
    await send(Div(ToolPanel(session_id=session_id), hx_swap_oob='true', id='toollist'))
    return

# %% ../nbs/05_chat_ui.ipynb 29
# Serve files from the 'data' directory
@app.get("/data/{file_name:path}")
async def get_file(file_name: str):
    """Serve files dynamically from the 'data' directory."""
    data_path = os.getenv("LLMCAM_DATA", "../data")
    file_path = Path(data_path) / file_name
    if file_path.exists():
        return FileResponse(file_path)
    return {"error": f"File '{file_name}' not found"}

# %% ../nbs/05_chat_ui.ipynb 31
import asyncio
import time

def llmcam_chatbot(
        host="0.0.0.0",  # The host to listen on
        port=5001,  # The port to listen on
    ):
    # Import app from chat_ui base module
    from llmcam.chat_ui import app

    # Initialize session tools and execute handler
    session_tools = {}
    globals()["session_tools"] = session_tools

    def execute_handler(
        function_name: str,  # Name of the function to execute
        session_id: str,  # Session ID to use
        **kwargs,  # Additional arguments to pass to the function
    ):
        tools = session_tools[session_id]
        return execute_handler_core(tools, function_name, **kwargs)
    
    globals()["execute_handler"] = execute_handler
    
    server = uvicorn.Server(uvicorn.Config(app, host=host, port=port))
    async def async_run_server(server): await server.serve()
    asyncio.run(async_run_server(server))
