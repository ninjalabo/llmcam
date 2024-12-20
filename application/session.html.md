# Browser session


<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

Concurrency should be taken into consideration in developing our web
application. Concurrency refers to the ability of the application to
handle multiple tasks or connections simultaneously, without blocking or
waiting for other tasks to complete. This is crucial for ensuring that
the service remains responsive and scalable, especially when serving a
large number of users.

However, with our current framework, there are multiple functions that
utilize global variables, which will be shared from the server-side.
This can cause significant issues in a concurrent environment, such as
race conditions, where multiple tasks or connections attempt to read and
modify the same variable simultaneously. This may lead to unpredictable
behavior, data corruption, or incorrect results. For instance, if two
users’ requests depend on the same global variable being updated, the
updates might overwrite each other or produce inconsistent states,
affecting the reliability of the application.

Our current solution to this issue involves introducing the concept of
`session`. Each `session` represents one connection with a user browser
and all session-specific variables are stored in a higher-level mapping
of session ID to values. Our frameworks will also configured towards the
use of session.

## Session messages

As a chatbot application, we usually require the whole conversation
being pasted into chat history rather than using a single new message
for a smooth user experience. For simplication purpose, we introduce a
mock database for storing our `messages` list for each session:

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/session.py#L32"
target="_blank" style="float:right; font-size:smaller">source</a>

### retrieve_session_message

>  retrieve_session_message (session_id:str)

*Retrieve the messages for a given session_id*

## Session tools

One major utility in our framework that uses global variables is the
`llmcam.utils.store` module which updates the global tools list. To
configure this towards `session` framework, we can save the `tools`
instance (Python pointer) of each `session` and define a custom fixup
function that retrieves this instance and passes it to the actual
manager tools. The schema of these manager tools also require a new
`metadata` field called `session_id` for the fixup function to identify
the correct instance.

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/session.py#L40"
target="_blank" style="float:right; font-size:smaller">source</a>

### retrieve_session_tools

>  retrieve_session_tools (session_id:str)

*Retrieve the tools for a given session_id*

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/session.py#L46"
target="_blank" style="float:right; font-size:smaller">source</a>

### prepare_handler_schemas

>  prepare_handler_schemas (session_id:str, fixup:Callable=None)

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
<td>fixup</td>
<td>Callable</td>
<td>None</td>
<td>Optional function to fix up the execution</td>
</tr>
</tbody>
</table>

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/session.py#L55"
target="_blank" style="float:right; font-size:smaller">source</a>

### execute_handler

>  execute_handler (function_name:str, session_id:str, **kwargs)

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
<td>function_name</td>
<td>str</td>
<td>Name of the function to execute</td>
</tr>
<tr>
<td>session_id</td>
<td>str</td>
<td>Session ID to use</td>
</tr>
<tr>
<td>kwargs</td>
<td></td>
<td></td>
</tr>
</tbody>
</table>

## Session notifications

The notifications system is quite more complicated. It relies on also
subtools to pass in sub GPT in the separate thread running notification
stream. These subtools include a tool to send notification and a tool to
stop the stream. The default utilities function for this uses a common
global pointer `stream_thread`, which will not work in this case. Hence,
we need to implement the new utilities function:

- [`execute_send_notification`](https://ninjalabo.github.io/llmcam/application/session.html#execute_send_notification):
  Instead of implementing the actual function, a `fixup` is implemented
  to capitalize on the metadata field `session_id`. This function also
  utilizes the feature that a websocket sender function can be saved in
  global collections - [example with real time Chat
  App](https://docs.fastht.ml/explains/websockets.html#real-time-chat-app).
  Therefore, it simply retrieves the sender function with `session_id`
  and uses it to send the message.  
- [`execute_stopper`](https://ninjalabo.github.io/llmcam/application/session.html#execute_stopper):
  Instead of implementing the actual function, a `fixup` is implemented
  to capitalize on the metadata field `session_id` and `noti_id`. The
  idea is that each notification stream is given a unique ID and saved
  in a mapping of IDs to notification streams. This mapping is also
  retrievable by `session_id`.

We also need to implement a custom
[`start_notification_stream`](https://ninjalabo.github.io/llmcam/application/session.html#start_notification_stream)
function which will be used as a tool by GPT Function Calling. This
function will utilize `session_id` and create a unique `noti_id` to
define schemas for subtools with these values as metadata. It also
defines these schemas such that the `module` metadata is missing to
ensure the attached `fixup` function will be called instead. However,
because it uses a metadata field `session_id`, it will also need to have
a `fixup` function.

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/session.py#L68"
target="_blank" style="float:right; font-size:smaller">source</a>

### retrieve_session_notis

>  retrieve_session_notis (session_id:str)

*Retrieve the notification sender and streams for a given session_id*

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/session.py#L73"
target="_blank" style="float:right; font-size:smaller">source</a>

### set_noti_sender

>  set_noti_sender (session_id:str, noti_sender:Callable)

*Set the notification sender for a given session_id*

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/session.py#L111"
target="_blank" style="float:right; font-size:smaller">source</a>

### prepare_stopper_schema

>  prepare_stopper_schema (session_id:str)

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/session.py#L94"
target="_blank" style="float:right; font-size:smaller">source</a>

### prepare_sender_schema

>  prepare_sender_schema (session_id:str)

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/session.py#L79"
target="_blank" style="float:right; font-size:smaller">source</a>

### execute_send_notification

>  execute_send_notification (function_name, session_id, msg, **kwargs)

*Fixup function to send a notification.*

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/session.py#L86"
target="_blank" style="float:right; font-size:smaller">source</a>

### execute_stopper

>  execute_stopper (function_name, session_id, noti_id, **kwargs)

*Fixup function to stop a notification stream.*

Implementation of custom
[`start_notification_stream`](https://ninjalabo.github.io/llmcam/application/session.html#start_notification_stream):

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/session.py#L133"
target="_blank" style="float:right; font-size:smaller">source</a>

### start_notification_stream

>  start_notification_stream (session_id:str, messages:list)

*Start a notification stream to monitor a process described in
messages.*

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
<tr>
<td>messages</td>
<td>list</td>
<td>All the previous messages in the conversation</td>
</tr>
</tbody>
</table>

Define the `fixup` function for starting a notification stream which
passes in `session_id` to
[`start_notification_stream`](https://ninjalabo.github.io/llmcam/application/session.html#start_notification_stream).
Define also a function to attach `session_id` as metadata for the
notification FC schema and attach the `fixup` function.

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/session.py#L189"
target="_blank" style="float:right; font-size:smaller">source</a>

### execute_start_notification_stream

>  execute_start_notification_stream (function_name, session_id, messages,
>                                         **kwargs)

*Fixup function to start a notification stream.*

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/session.py#L179"
target="_blank" style="float:right; font-size:smaller">source</a>

### prepare_notification_schemas

>  prepare_notification_schemas (session_id:str, fixup:Callable=None)

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
<td>fixup</td>
<td>Callable</td>
<td>None</td>
<td>Optional function to fix up the execution</td>
</tr>
</tbody>
</table>

## Setup

Implement some utilities to manage all session-related data:

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/session.py#L208"
target="_blank" style="float:right; font-size:smaller">source</a>

### init_session

>  init_session (session_id:Optional[str]=None)

------------------------------------------------------------------------

<a
href="https://github.com/ninjalabo/llmcam/blob/main/llmcam/application/session.py#L226"
target="_blank" style="float:right; font-size:smaller">source</a>

### remove_session

>  remove_session (session_id:str)

*Remove the session with the given session_id*