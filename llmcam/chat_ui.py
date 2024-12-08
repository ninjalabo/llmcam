"""chat UI implemented in fastHTML"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/05_chat_ui.ipynb.

# %% auto 0
__all__ = ['session_messages', 'session_tools', 'session_notis', 'default_tools', 'hdrs', 'app', 'noti_script', 'scroll_script',
           'title_script', 'prepare_handler_schemas', 'execute_handler', 'execute_send_notification', 'execute_stopper',
           'prepare_stopper_schema', 'start_notification_stream', 'prepare_notification_schemas',
           'execute_start_notification_stream', 'init_session', 'ChatMessage', 'ChatInput', 'ActionButton',
           'ActionPanel', 'ToolPanel', 'NotiMessage', 'NotiButton', 'index', 'noti_disconnect', 'wsnoti',
           'chat_disconnect', 'wschat', 'get_file', 'llmcam_chatbot']

# %% ../nbs/05_chat_ui.ipynb 4
import uvicorn
import uuid
import os
import asyncio
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
from .notification import notification_stream_core, process_notification_schema, StreamThread
from .bash_command import *

# %% ../nbs/05_chat_ui.ipynb 6
# Set up database for information per session
session_messages = {}  # Messages for each session
session_tools = {}  # Tools for each session
session_notis = {}  # Sender and notification streams for each session

# %% ../nbs/05_chat_ui.ipynb 7
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

# %% ../nbs/05_chat_ui.ipynb 9
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

# %% ../nbs/05_chat_ui.ipynb 11
# Utility functions to manage notifications per session
def execute_send_notification(function_name, session_id, msg, **kwargs):
    """Fixup function to send a notification."""
    global session_notis
    sender, _ = session_notis[session_id]  # Get the sender
    sender(msg)
    return 'Notification sent'

def execute_stopper(function_name, session_id, noti_id, **kwargs):
    """Fixup function to stop a notification stream."""
    global session_notis
    _, notis = session_notis[session_id]  # Get the notification streams 
    notis[noti_id].stop()  # Stop the stream with the given ID
    return 'Notification stream stopped'

def prepare_stopper_schema(session_id: str):
    return {
        'type': 'function',
        'function': {
            'name': 'stop_notification',
            'description': 'Stop the notification stream',
            'parameters': {
                'type': 'object', 
                'properties': {
                    'noti_id': {
                        'type': 'string', 
                        'description': 'Unique UUID of the notification stream to stop, provided when the stream was started'}
                }, 
                'required': ['noti_id']},
            'metadata': {
                'session_id': session_id,
            },
            'fixup': f"{execute_stopper.__module__}.{execute_stopper.__name__}"
        }
    }

def start_notification_stream(
    session_id: str,  # Session ID to use
    messages: list,  # All the previous messages in the conversation
):
    """Start a notification stream to monitor a process described in messages."""
    global session_notis
    global session_tools

    _, notis = session_notis[session_id]  # Get the notification streams

    # Define a new notification stream with a unique ID
    noti_id = str(uuid.uuid4())
    
    # Describe the sender and stopper functions
    sender_schema = {
        'type': 'function',
        'function': {
            'name': 'send_notification',
            'description': 'Send a notification with a message',
            'metadata': {
                'session_id': session_id
            },
            'parameters': {'type': 'object',
                'properties': {'msg': {'type': 'string',
                'description': 'Notification message to send'}},
                'required': ['msg']},
            'fixup': f"{execute_send_notification.__module__}.{execute_send_notification.__name__}"
        },
    }

    stopper_schema = prepare_stopper_schema(session_id)

    # Define a function to start the stream
    def stream_starter(tools, messages):
        notis[noti_id] = StreamThread(noti_id, tools, messages)
        notis[noti_id].start()

    # Extract the tools for the session
    tools = session_tools[session_id]
    # Remove the stop_notification tool from the list of tools to avoid duplication
    tools = [ tool for tool in tools if tool['function']['name'] != 'stop_notification' ] 

    submessages = [ message for message in messages ]
    submessages.append(form_msg(
        'system',
        f'Notification stream started with ID {noti_id}. Complete the stream here.'
    ))

    # Start the notification stream
    notification_stream_core(
        tools, 
        submessages,
        stream_starter=stream_starter,
        send_notification_schema=sender_schema,
        stream_stopper_schema=stopper_schema
    )

    # Return the ID of the notification stream  
    return f"Notification stream started with ID {noti_id}" 

# %% ../nbs/05_chat_ui.ipynb 13
def prepare_notification_schemas(
        session_id: str,  # Session ID to use
        fixup: Callable = None,  # Optional function to fix up the execution
    ):  # Prepare the notification schema
    schema = process_notification_schema(start_notification_stream)  # Get the schema for starting notification stream
    # Set additional metadata
    schema['function']['metadata']['session_id'] = session_id  
    if fixup: schema['function']['fixup'] = f"{fixup.__module__}.{fixup.__name__}"
    return schema

def execute_start_notification_stream(function_name, session_id, messages, **kwargs):
    """Fixup function to start a notification stream."""
    return start_notification_stream(session_id, messages)

# %% ../nbs/05_chat_ui.ipynb 14
def init_session(session_id: Optional[str] = None):
    if session_id is None or session_id not in session_messages:
        # Initialize tools in session tools and create a session ID
        session_id = str(uuid.uuid4())

        # Add default tools, prepare handler schemas, prepare notification schemas, and prepare stopper schema
        session_tools[session_id] = []
        session_tools[session_id].extend(prepare_handler_schemas(session_id, execute_handler))
        session_tools[session_id].extend(default_tools)
        session_tools[session_id].append(prepare_notification_schemas(session_id, execute_start_notification_stream))
        session_tools[session_id].append(prepare_stopper_schema(session_id))

        # Initialize messages in session messages
        session_messages[session_id] = []
    
    return session_id

# %% ../nbs/05_chat_ui.ipynb 16
# Set up the app, including daisyui and tailwind for the chat component
hdrs = (picolink,
        Link(rel="icon", href=f"""{os.getenv("LLMCAM_DATA", "../data").split("/")[-1]}/favicon.ico""", type="image/png"),
        Script(src="https://cdn.tailwindcss.com"),
        Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css"),
        # Link(rel="preconnect", href="https://fonts.googleapis.com"),
        # Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=""),
        # Link(href="https://fonts.googleapis.com/css2?family=Patrick+Hand", rel="stylesheet"),
        Script(src="https://unpkg.com/htmx.org"),
        Style("p {color: black; font-family: 'Georgia', Times, serif;}"),
        Style("li {color: black; font-family: 'Georgia', Times, serif;}"),
        Style("main {font-family: 'Georgia', Times, serif;}"),
        MarkdownJS(), HighlightJS(langs=['python', 'javascript', 'html', 'css']))
app = FastHTML(hdrs=hdrs, exts="ws")

# %% ../nbs/05_chat_ui.ipynb 18
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

# %% ../nbs/05_chat_ui.ipynb 21
# The input field for the user message. Also used to clear the
# input field after sending a message via an OOB swap
def ChatInput():  # Returns an input field for the user message
    return Input(name='msg', id='msg-input', placeholder="Type a message",
                 cls="input input-bordered w-full rounded-l-2xl", 
                 hx_swap_oob='true'  # Re-render the element to remove submitted message
                )

# %% ../nbs/05_chat_ui.ipynb 24
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
            style="font-family: 'Georgia', Times, serif;" 
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
        A('YouTube Playlist (Examples)', href='https://www.youtube.com/watch?v=BuyqWfyhvgE&list=PLNzPo4P4-KZOJEwDrywdUt8IryV06viqg&index=8', target='_blank'),

        cls="flex flex-col h-fit gap-4 py-4 px-4"
    )

# %% ../nbs/05_chat_ui.ipynb 28
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
        Ul(*items, cls="list-disc list-inside px-6", style="max-height: 60vh; overflow-y:auto;"),
        id="toollist",
        cls="flex flex-col h-fit gap-4 py-4 px-4"
    )

# %% ../nbs/05_chat_ui.ipynb 31
def NotiMessage(
        message: str = "No message"  # Message to display
    ):  # Returns a notification message hidden from the UI view
    return Hidden(message, id="notification", cls="text-black")

def NotiButton(
        session_id: str  # Session ID to use
    ):  # Returns a hidden button to trigger notification websocket connection
    return Form(
        ws_send=True,
        hx_ext='ws', ws_connect='/wsnoti',
        style="display: none;"
    )(
        Hidden(session_id, name="session_id"),
        Button(
            "Notification", 
            id="connect-btn", 
            cls="btn btn-primary rounded-2 h-fit", 
            style="display: none;"
        )
    )

# %% ../nbs/05_chat_ui.ipynb 32
# Event listener to handle notifications when the element #notification is loaded
noti_script = Script("""
    // Automatically click the hidden button to connect to the notification websocket
    window.addEventListener('load', function() {
        let connectButton = document.querySelector('#connect-btn');
        if (connectButton) {
            connectButton.click();
            console.log("Hidden button clicked on page load!");
        }
    });
                     
    // Listen for the htmx:load event on the document body
    document.body.addEventListener('htmx:load', function(event) {
        if (event.target.id === "notification") {
            let htDivElement = event.detail.elt; // Extract the HtDiv element

            // Find the input element inside the HtDiv and extract its value
            let inputElement = htDivElement.querySelector('input');
            if (inputElement) {
                let inputValue = inputElement.value;
                alert(inputValue);
            } else {
                console.log("Input element not found.");
            }
        }
    });
""")

# %% ../nbs/05_chat_ui.ipynb 35
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

# %% ../nbs/05_chat_ui.ipynb 36
title_script = Script("""
    // Function to set the title of the page
    document.title = "LLMCAM";
""")

# %% ../nbs/05_chat_ui.ipynb 38
@app.get('/')
async def index(session):
    # Initialize the session
    session_id = init_session(session_id=session.get('session_id'))
    
    # Set up the chat UI
    sidebar = Div(
        ActionPanel(session_id=session_id),
        ToolPanel(session_id=session_id),
        NotiButton(session_id=session_id),
        NotiMessage(),
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
                    Button("Send", cls="btn btn-primary rounded-r-2xl"),
                    style="font-family: 'Georgia', Times, serif;"
                )
            ),
            scroll_script
        ),
    )
    return Main(
        noti_script,
        title_script,
        sidebar,
        #a('Click here', href='https://example.com', target='_blank'),
        page, 
        title="Chatbot",
        data_theme="wireframe",
        cls="h-[100vh] w-full relative flex flex-row items-stretch overflow-hidden transition-colors z-0 p-0",)

# %% ../nbs/05_chat_ui.ipynb 40
def noti_disconnect(ws):
    """Remove session ID from session notification sender on websocket disconnect"""
    session_id = ws.scope.get("session_id")
    if session_id in session_notis:
        _, notis = session_notis[session_id]
        for noti in notis.values():
            noti.stop()
        del session_notis[session_id]

# %% ../nbs/05_chat_ui.ipynb 41
@app.ws('/wsnoti')
async def wsnoti(ws, send, session_id: str):
    # Initialize the session
    session_id = init_session(session_id=session_id)

    # Set the session ID in the websocket scope
    ws.scope["session_id"] = session_id

    # Set up the notification sender for the session
    def send_noti(message):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:  # No current event loop in this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    
        if loop.is_running():
            # Schedule the task on the running loop
            asyncio.create_task(send(Div(NotiMessage(message), id="notification", hx_swap_oob="true")))
        else:
            # Create and run a new loop
            loop.run_until_complete(send(Div(NotiMessage(message), id="notification", hx_swap_oob="true")))
    
    session_notis[session_id] = (send_noti, {})

    # Send a notification to the client
    send_noti("Notification service enabled.")

# %% ../nbs/05_chat_ui.ipynb 45
# On websocket disconnect, remove the session ID from the session messages and tools
def chat_disconnect(ws):
    """Remove session ID from session messages and tools on websocket disconnect"""
    session_id = ws.scope.get("session_id")
    if session_id in session_messages:
        del session_messages[session_id]
    if session_id in session_tools:
        del session_tools[session_id]

# %% ../nbs/05_chat_ui.ipynb 46
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
`../data/<filename>` in Markdown syntax. \
When asked to monitor or notify about a process, start a detached notification stream and do not \
wait for it to stop in chat response.\
Use the available tools to stop stream or send notifications from the stream."))
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

# %% ../nbs/05_chat_ui.ipynb 48
# Serve files from the 'data' directory
@app.get("/data/{file_name:path}")
async def get_file(file_name: str):
    """Serve files dynamically from the 'data' directory."""
    data_path = os.getenv("LLMCAM_DATA", "../data")
    file_path = Path(data_path) / file_name
    if file_path.exists():
        return FileResponse(file_path)
    return {"error": f"File '{file_name}' not found"}

# %% ../nbs/05_chat_ui.ipynb 50
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
