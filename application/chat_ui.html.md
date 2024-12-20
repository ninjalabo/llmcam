# Chat UI in fastHTML


<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

## Chat App initialization

Start by creating the chat application with `FastHTML`.

For running while testing with Jupyter notebook, use the `JupyUvi` in
`fasthtml` to run in separate thread.

``` python
from fasthtml.jupyter import *

server = JupyUvi(app=app)
```

<script>
document.body.addEventListener('htmx:configRequest', (event) => {
    if(event.detail.path.includes('://')) return;
    htmx.config.selfRequestsOnly=false;
    event.detail.path = `${location.protocol}//${location.hostname}:8000${event.detail.path}`;
});
</script>

``` python
server.stop()
```

## Chat components

Basic chat UI components can include Chat Message and a Chat Input. For
a Chat Message, the important attributes are the actual message (str)
and the role of the message owner (user - boolean value whether the
owner is the user, not the AI assistant).

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/chat_ui.py#L35"
target="_blank" style="float:right; font-size:smaller">source</a>

### ChatMessage

>  ChatMessage (msg:str, user:bool)

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
<td>msg</td>
<td>str</td>
<td>Message to display</td>
</tr>
<tr>
<td>user</td>
<td>bool</td>
<td>Whether the message is from the user or assistant</td>
</tr>
</tbody>
</table>

For the chat input, set the name for submitting a new message via form.

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/chat_ui.py#L53"
target="_blank" style="float:right; font-size:smaller">source</a>

### ChatInput

>  ChatInput ()

### Action Buttons

Simple actions for creating a new message from the user side.

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/chat_ui.py#L60"
target="_blank" style="float:right; font-size:smaller">source</a>

### ActionButton

>  ActionButton (session_id:str, content:str, message:str=None)

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
<td>session_id</td>
<td>str</td>
<td></td>
<td>Session ID to use</td>
</tr>
<tr>
<td>content</td>
<td>str</td>
<td></td>
<td>Text to display on the button</td>
</tr>
<tr>
<td>message</td>
<td>str</td>
<td>None</td>
<td>Message to send when the button is clicked</td>
</tr>
</tbody>
</table>

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/chat_ui.py#L79"
target="_blank" style="float:right; font-size:smaller">source</a>

### ActionPanel

>  ActionPanel (session_id:str)

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
<td>session_id</td>
<td>str</td>
<td>Session ID to use</td>
</tr>
</tbody>
</table>

### Tools panel

Sidebar-panel for displaying current list of available (loaded) tools in
a user-session.

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/chat_ui.py#L94"
target="_blank" style="float:right; font-size:smaller">source</a>

### ToolPanel

>  ToolPanel (session_id:str)

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
<td>session_id</td>
<td>str</td>
<td>Session ID to use</td>
</tr>
</tbody>
</table>

### Notifications

The idea of sending notifications from a background task / websocket
with FastHTML is to send an HTMX update, then detect and extract
information from the event via a document event listener.

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/chat_ui.py#L122"
target="_blank" style="float:right; font-size:smaller">source</a>

### NotiButton

>  NotiButton (session_id:str)

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
<td>session_id</td>
<td>str</td>
<td>Session ID to use</td>
</tr>
</tbody>
</table>

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/chat_ui.py#L117"
target="_blank" style="float:right; font-size:smaller">source</a>

### NotiMessage

>  NotiMessage (message:str='No message')

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
<td>message</td>
<td>str</td>
<td>No message</td>
<td>Message to display</td>
</tr>
</tbody>
</table>

## Router

### Home page

The home page should contain our message list and the Chat Input. The
main page can be extracted by accessing the index (root) endpoint.

``` python
def click_here(): return a('Click here', href='https://example.com', target='_blank')
```

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/chat_ui.py#L195"
target="_blank" style="float:right; font-size:smaller">source</a>

### index

>  index (session)

### Notification websockets

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/chat_ui.py#L242"
target="_blank" style="float:right; font-size:smaller">source</a>

### noti_disconnect

>  noti_disconnect (ws)

*Remove session ID from session notification sender on websocket
disconnect*

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/chat_ui.py#L249"
target="_blank" style="float:right; font-size:smaller">source</a>

### wsnoti

>  wsnoti (ws, send, session_id:str)

Test usage:

``` python
#first_noti_sender = list(session_notis.values())[0][0]
#first_noti_sender("Test message.")
```

### Chat websockets

When connecting to websockets for chat, this function should:

- Extract the new and all previous chat history  
- Prompt & get answers from ChatGPT from all these messages  
- Return a new ChatMessage

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/chat_ui.py#L278"
target="_blank" style="float:right; font-size:smaller">source</a>

### chat_disconnect

>  chat_disconnect (ws)

*Remove session ID from session messages and tools on websocket
disconnect*

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/chat_ui.py#L286"
target="_blank" style="float:right; font-size:smaller">source</a>

### wschat

>  wschat (ws, msg:str, send, session_id:str)

### Static files

In case the user needs to display images, serves files from directory
`../data`.

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/chat_ui.py#L326"
target="_blank" style="float:right; font-size:smaller">source</a>

### get_file

>  get_file (file_name:str)

*Serve files dynamically from the ‘data’ directory.*