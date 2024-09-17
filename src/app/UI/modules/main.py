"""
Main UI module.

:author: Max Milazzo
"""


import multiprocessing
from app.API.message import service, transmit
from app.util import config, display
from app.util.channel import Channel, channel_search
from app.util.media import Attachment
from tkinter import Button, filedialog, Label, OptionMenu, StringVar, Text, Tk, ttk
from typing import Union


service_process = None
# specify current main API service process globally


attachments = []
# list of attachments to be sent with current message


def start_service(
    channel: Union[Channel, None], discord_cids: list, auth: dict
) -> Union[multiprocessing.Process, None]:
    """
    Starts API service.

    :param channel: channel object to start service on
    :param disc_cids: list of Discord channel IDs to send messages to
    :param auth: Discord authentication credentials
    :return: API service process (or None on failure)
    """
    
    if channel is None:
        return None
        # return None on failure
    
    service_process = multiprocessing.Process(
        target=service.start, args=(
            channel, discord_cids, auth
        )
    )
    service_process.start()
    # create and start service
    
    return service_process
    

def clear() -> None:
    """
    Clears message input and empties attachments.
    """

    global attachments

    message_input.delete("1.0", "end-1c")
    # reset global message input widget
    
    attachments = []
    attachments_label.forget()
    # reset global attachments list and display label

    
def send_message(
    tag: str, message_input: Text, channel_sel: StringVar, channels: list, 
    webhooks: list
) -> None:
    """
    Handles and sends message to server.

    :param tag: user self-ID tag
    :param message_input: message input widget
    :param channel_sel: channel selection variable
    :param channels: list of all available channel objects
    :param webhooks: list of all available webhook objects
    """

    channel_name = channel_sel.get()
    # get channel name from channel selection variable
    
    if channel_name == "":
        return
        # return on empty channel (no selection)
        
    channel = channel_search(channels, channel_name)
    # search for channel object by name
    
    message_text = message_input.get("1.0", "end-1c").rstrip()
    # extract message text from input widget
    
    if message_text == "" and len(attachments) == 0:
        return
        # return on empty message and no attachments
    
    transmit.send(tag, message_text, channel, webhooks, attachments)
    # send message to server

    clear()
    # clear message data


def channel_select(
    channel_name: str, channels: list, discord_cids: list, auth: dict
) -> None:
    """
    Change current active channel selection.
    
    :param channel_name: channel name to select
    :param channels: list of all available channel objects
    :param disc_cids: list of available Discord channel IDs
    :param auth: Discord authentication credentials
    """
    
    global service_process
    
    channel = channel_search(channels, channel_name)
    # search for channel object by name
    
    display.clear()
    
    if service_process is not None:
        service_process.terminate()
        # terminate current service process
        
    service_process = start_service(channel, discord_cids, auth)
    # start new API service process


def attach_files() -> None:
    """
    Attach files to message.
    """

    global attachments

    filepaths = filedialog.askopenfilenames()
    # get attachment filepaths

    for path in filepaths:
        with open(path, "rb") as f:
            raw_data = f.read()
            # read attachment file byte data

        attachments.append(
            Attachment(raw_data, path=path)
        )
        # add attachments to global list

    attachment_basenames = [
        "<attachment \"{}\">".format(
            attachment.filename
        ) for attachment in attachments
    ]
    # create attachment display labels

    attachments_label_text = "\n".join(attachment_basenames)
    # generate attachment display label text

    if len(attachments) > 0:
        attachments_label.config(text=attachments_label_text)
        attachments_label.pack(padx=2, side="left")
        # display attachments (if any)
    

def on_close(root: Tk) -> None:
    """
    Handle main window close event.

    :param root: main window
    """

    if service_process is not None:
        service_process.terminate()
        # terminate current service process

    root.destroy()
    # close main window


user_config, server_config, channels = config.load()
# read configuration files and fetch channels

tag = user_config["tag"]
discord_cids = server_config["channels"]
auth = user_config["auth"]
webhooks = server_config["webhooks"]
# extract relavent configuration data (for readability)

root = Tk()
root.attributes("-topmost", True)
root.title("Discord CipherChat")
# configre main window

title_frame = ttk.Frame(root)
toolbar_frame = ttk.Frame(root)

title_label = Label(title_frame, text="New Message")
# create "new message" title label

title_frame.pack(side="top")
toolbar_frame.pack(side="bottom", fill="x")

clicked = StringVar()
clicked.trace_add(
    "write", lambda *_,
    var=clicked: channel_select(var.get(), channels, discord_cids, auth)
)
# create channel selection variable and trace it to update channel selection

if len(channels) > 0:
    clicked.set(channels[0].name)
    channel_drop = OptionMenu(toolbar_frame, clicked, *channels)
    # configure initial channel selection

else:
    channel_drop = OptionMenu(toolbar_frame, clicked, "")
    channel_drop["menu"].delete(0)
    # configure empty channel selection

channel_label = Label(toolbar_frame, text="Channel:")
# create channel title label

options_button = Button(toolbar_frame, text=" ≡ ")
options_button["state"] = "disabled"
# create and configure main menu selection options button

message_input = Text(root, height=5, width=35)
message_input.pack(side="top", fill="both", expand=True, padx=2)
# create and configure message input widget

attachments_label = Label(root, justify="left")
# create (but do not yet add to display) attachments information label

send_button = Button(
    toolbar_frame, text="Send",
    command=lambda: send_message(
        tag, message_input, clicked, channels, webhooks
    )
)
# create send button

clear_button = Button(toolbar_frame, text="Clear", command=clear)
# create clear button

attachment_button = Button(toolbar_frame, text=" + ", command=attach_files)
# create attachment add button

title_label.pack(pady=5)
send_button.pack(side="left", padx=2, pady=2)
clear_button.pack(side="left", padx=2, pady=2)
attachment_button.pack(side="left", padx=2, pady=2)
options_button.pack(side="right", padx=2, pady=2)
channel_drop.pack(side="right", pady=2)
channel_label.pack(side="right", padx=(20, 0), pady=2)
# place remaining elements

root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))
# configure custom main window close event