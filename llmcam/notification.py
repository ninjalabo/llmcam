"""This notebook implement notification workflow"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/15_notification.ipynb.

# %% auto 0
__all__ = ['StreamThread', 'notification_stream_core', 'default_stream_starter', 'default_stream_stopper',
           'process_notification_schema']

# %% ../nbs/15_notification.ipynb 3
from threading import Thread, Event
import time
from typing import Optional, Callable
from .fn_to_fc import complete, tool_schema

# %% ../nbs/15_notification.ipynb 4
# Define the stream thread class
class StreamThread(Thread):
    def __init__(self, thread_id, tools, messages):
        super().__init__()
        self.thread_id = thread_id
        self.stop_event = Event()
        self.tools = tools
        self.messages = messages

    def run(self):
        while not self.stop_event.is_set():
            complete(self.messages, tools=self.tools)
            time.sleep(5)

    def stop(self):
        self.stop_event.set()

# %% ../nbs/15_notification.ipynb 5
def notification_stream_core(
    tools: list,  # Tools to use
    send_notification: Callable,  # Function to send the notification
    messages: list,  # Previous conversation with the user
    stream_starter: Optional[Callable] = None,  # Function to start the stream
    stream_stopper: Optional[Callable] = None  # Function to stop the stream
) -> str:
    """Core function to start and stop the notifications stream"""
    # Copy the messages to avoid modifying the original list
    submessages = [ message for message in messages ]

    # Add sending notification services to tool schema
    subtools = [ tool for tool in tools if tool['function']['name'] != 'start_notification_stream' ]
    subtools.append(tool_schema(send_notification, 'send_notification'))
    subtools.append(tool_schema(stream_stopper, 'send_notification'))

    # Start the notifications stream
    stream_starter(subtools, submessages)

    return 'Notifications stream started'

# %% ../nbs/15_notification.ipynb 6
def default_stream_starter(tools, messages):
    """Default function to start the notifications stream"""
    global stream_thread

    # Start the notifications stream
    stream_thread = StreamThread(1, tools, messages)
    stream_thread.start()

def default_stream_stopper():
    """Default function to stop the notifications stream"""
    global stream_thread

    # Stop the notifications stream
    stream_thread.stop()
    stream_thread.join()

# %% ../nbs/15_notification.ipynb 7
def process_notification_schema(
    start_notifications_stream: Callable,  # Function to start the notifications stream
):
    """Process the notification schema"""
    notification_schema = tool_schema(start_notifications_stream, 'notification')

    notification_schema['function']['parameters'] = {
        'type': 'object',
        'properties': {
            'messages': {
                'description': 'All the previous messages in the conversation',
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'role': {
                            'type': 'string',
                            'enum': ['user', 'tool', 'system', 'assistant']
                        },
                        'content': {
                            'type': 'string'
                        }
                    }
                }
            }
        }
    }
    return notification_schema
