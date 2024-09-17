"""
New channel creation UI component.

:author: Max Milazzo
"""


import tkinter as tk
from app.UI.modules import main
from app.util.channel import Channel, channel_search
from tkinter import Button, END, Entry, Label, messagebox, Tk, Toplevel, ttk
from typing import Union


def channel_name_valid(channel_name: str) -> bool:
    """
    Ensures a channel name is valid.

    :param channel_name: channel name string to check
    :return: True if channel name is valid, False otherwise
    """

    if channel_name == "":
        messagebox.showerror(
            "Name Error",
            "Channel names must include 1 or more visible symbols."
        )
        return False
        # empty string invalid
        
    check = channel_search(main.channels, channel_name)

    if check is not None:
        messagebox.showerror(
            "Name Error",
            f'Channel with name "{channel_name}" already exists in your feed.'
        )
        return False
        # channel name already exists (invalid)
    
    return True


def create_channel(
    channel_name_entry: Entry, new_channel: Union[Channel, None] = None
) -> bool:
    """
    Creates a new channel.

    :param channel_name_entry: channel name entry widget
    :param new_channel: channel object to create (if None provided, a new
        channel object will be created with the provided channel name)
    :return: True if channel was created, False otherwise
    """
    
    raw_channel_name = channel_name_entry.get()   
    channel_name = raw_channel_name.strip()
    # extract channel name

    if not channel_name_valid(channel_name):
        return False
        # exit on invalid name

    if new_channel is None:
        new_channel = Channel(channel_name)
        # create new channel object
    
    else:
        new_channel.name = channel_name
        # set channel name
        
    main.channels.append(new_channel)
    # add channel to data
    
    main.channel_drop["menu"].add_command(
        label=new_channel, command=tk._setit(main.clicked, new_channel)
    )
    # add channel to UI dropdown
    
    main.clicked.set(new_channel)
    channel_name_entry.delete(0, END)
    # set current channel to new channel and clear entry widget

    return True


def open_new_channel_window(new_channel: Union[Channel, None] = None) -> None:
    """
    Opens a new channel creation window.
    
    :param new_channel: channel object to create
    """

    x, y = main.root.winfo_pointerxy()
    
    if new_channel is None:
        new_channel_window = Toplevel(main.root)
        new_channel_window.title("Create Channel")
        make_text = "Create"
        # create a new Toplevel window for entering the channel name
        
    else:
        new_channel_window = Tk()
        new_channel_window.title("Join Channel")
        make_text = "Join"
        # create a new Tk window for entering the channel name

    new_channel_window.geometry(f"250x85+{x}+{y}")
    # set geometry
        
    new_channel_window.attributes("-topmost", True)
    # specify "topmost" attribute
    
    ntitle_frame = ttk.Frame(new_channel_window)
    ntoolbar_frame = ttk.Frame(new_channel_window)

    ntitle_label = Label(ntitle_frame, text="New Channel")
    # create main title label

    ntitle_frame.pack(side="top")
    ntoolbar_frame.pack(side="bottom", fill="x")

    channel_name_entry = Entry(new_channel_window)
    channel_name_entry.pack(side="top", fill="both", padx=2)
    # create channel name entry windget
    
    if new_channel is not None:
        channel_name_entry.insert(0, new_channel.name)
        
        def create_func():
            """
            Custom creation function.
            """
            
            created = create_channel(channel_name_entry, new_channel)

            if created:
                new_channel_window.destroy()
                # destroy window on success
            
    else:
        create_func = lambda: create_channel(channel_name_entry, new_channel)
        # custom creation function

    create_button = Button(
        ntoolbar_frame, text=make_text, command=create_func
    )
    # create channel button
    
    nclear_button = Button(
        ntoolbar_frame, text="Clear",
        command=lambda: channel_name_entry.delete(0, END)
    )
    # clear entry text button
    
    create_button.pack(side="left", padx=2, pady=2)
    nclear_button.pack(side="left", padx=2, pady=2)
    ntitle_label.pack(pady=5)
    # place elements
    
    new_channel_window.mainloop()
    # necessary when new channel window is of type Tk