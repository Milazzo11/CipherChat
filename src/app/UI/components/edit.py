"""
Channel edit UI component.

:author: Max Milazzo
"""


import tkinter as tk
from app.UI.components.new import channel_name_valid
from app.UI.modules import main
from app.util.channel import channel_search
from tkinter import Button, END, Entry, Label, Listbox, messagebox, Scrollbar, Toplevel, ttk


def apply_changes(edit_listbox: Listbox) -> None:
    """
    Applies channel changes globally from values set in the edit window.

    :param edit_listbox: channel edit listbox
    """

    main.channel_drop["menu"].delete(0, END)
    # clear main channel dropdown

    new_channels = []

    for entry in edit_listbox.get(0, END):
        channel = channel_search(main.channels, entry)

        if channel is not None:
            new_channels.append(channel)
            main.channel_drop["menu"].add_command(
                label=entry,
                command=tk._setit(main.clicked, entry)
            )
            # add channels in new order to main channel dropdown

    main.channels = new_channels
    # set global channels storage variable to newly ordered channels list


def apply_rename(
    channel_name_entry: Entry, cur_name: str, edit_listbox: Listbox,
    rename_channel_window: Toplevel
) -> None:
    """
    Applies channel name change.

    :param channel_name_entry: channel name entry widget
    :param cur_name: current (non-changed) channel name
    :param edit_listbox: channel edit listbox
    :param rename_channel_window: channel rename window
    """

    new_name_raw = channel_name_entry.get()
    new_name = new_name_raw.strip()
    # get new channel name

    if not channel_name_valid(new_name):
        return
        # exit on invalid name

    for index, channel in enumerate(main.channels):
        if channel.name == cur_name:
            main.channels[index].name = new_name
            edit_listbox.delete(index)
            edit_listbox.insert(index, new_name)
            # update channel name

    apply_changes(edit_listbox)
    # apply changes globally

    if cur_name == main.clicked.get():
        main.clicked.set(new_name)
        # reset the currently selected channel name if needed

    rename_channel_window.destroy()
    # close rename channel window on successful renaming


def move_channel(edit_listbox: Listbox, direction: str) -> str:
    """
    Moves a channel up or down the selection list.

    :param edit_listbox: channel edit listbox
    :param direction: "up" or "down"

    :return: "break" to specify that no further key input taken after return
    """

    selected_index = edit_listbox.curselection()
    # get current selected channel index

    if direction == "up":
        if selected_index and selected_index[0] > 0:
            new_index = selected_index[0] - 1
            # set "up" new (moving to) index

        else:
            return "break"
            # return if item cannot be moved up

    else:
        if selected_index and selected_index[0] < edit_listbox.size() - 1:
            new_index = selected_index[0] + 1
            # set "down" new (moving to) index

        else:
            return "break"
            # return if item cannot be moved down

    selected_item = edit_listbox.get(selected_index)
    # get selected channel "item"

    edit_listbox.delete(selected_index)
    edit_listbox.insert(new_index, selected_item)
    edit_listbox.selection_clear(0, END)
    edit_listbox.selection_set(new_index)
    edit_listbox.activate(new_index)
    edit_listbox.see(new_index)
    # apply changes globally

    apply_changes(edit_listbox)
    # apply

    return "break"


def open_rename_window(edit_listbox: Listbox) -> None:
    """
    Opens channel rename window.

    :param edit_listbox: channel edit listbox
    """

    selected_index = edit_listbox.curselection()
    # get current selected channel index

    name = edit_listbox.get(selected_index)
    # get selected channel name

    rename_channel_window = Toplevel(main.root)
    # create a new window for renaming the channel

    x, y = main.root.winfo_pointerxy()
    rename_channel_window.geometry(f"260x85+{x}+{y}")
    # set window geometry specifications

    rename_channel_window.attributes("-topmost", True)
    rename_channel_window.title("Rename Channel")
    # set channel attributes

    ntitle_frame = ttk.Frame(rename_channel_window)
    ntoolbar_frame = ttk.Frame(rename_channel_window)
    ntitle_frame.pack(side="top")
    ntoolbar_frame.pack(side="bottom", fill="x")
    # divide into two frames

    ntitle_label = Label(ntitle_frame, text=f'Rename "{name}"')
    ntitle_label.pack(pady=5)
    # add "rename" title label

    channel_name_entry = Entry(rename_channel_window)
    channel_name_entry.pack(side="top", fill="both", padx=2)
    # add rename text entry

    rename_button = Button(
        ntoolbar_frame,
        text="Rename",
        command=lambda: apply_rename(
            channel_name_entry, name, edit_listbox, rename_channel_window
        )
    )
    
    rename_button.pack(side="left", padx=2, pady=2)
    # add rename button

    nclear_button = Button(
        ntoolbar_frame, text="Clear",
        command=lambda: channel_name_entry.delete(0, END)
    )
    nclear_button.pack(side="left", padx=2, pady=2)
    # add text clear button


def show_info(edit_listbox: Listbox) -> None:
    """
    Display channel information.

    :param edit_listbox: channel edit listbox
    """

    messagebox.showinfo(
        title="Information",
        message=(
            str(edit_listbox.size()) + " Active Channels:\n\n" +
            str(edit_listbox.get(0, END)))
        )


def open_edit_window() -> None:
    """
    Opens channel edit window.
    """

    x, y = main.root.winfo_pointerxy()

    edit_window = Toplevel(main.root)
    edit_window.attributes("-topmost", True)
    edit_window.title("Edit Channels")
    # create a new Toplevel window for editing channels

    ntitle_frame = ttk.Frame(edit_window)
    ntoolbar_frame = ttk.Frame(edit_window)

    edit_window.geometry(f"250x130+{x}+{y}")
    # set the geometry of the new channel window

    ntitle_label = Label(ntitle_frame, text="Channel List:")

    ntitle_frame.pack(side="top")
    ntoolbar_frame.pack(side="bottom", fill="x")

    edit_listbox = Listbox(edit_window, height=5, width=35)
    edit_listbox.pack(
        side="left", fill="both", expand=True, padx=2, pady=(0, 2)
    )
    # create edit ListBox

    scrollbar = Scrollbar(edit_window, command=edit_listbox.yview)
    scrollbar.pack(side="right", fill="y")
    edit_listbox.config(yscrollcommand=scrollbar.set)
    # put ListBox in Scrollbar

    for channel in main.channels:
        edit_listbox.insert(END, channel)

    edit_listbox.bind(
        "<Double-Button-1>",
        lambda _: open_rename_window(edit_listbox)
    )
    # bind the double click event to move channels within the Listbox

    move_up_button = Button(
        ntoolbar_frame, text=" " + chr(8593) + " ",
        command=lambda: move_channel(edit_listbox, "up")
    )
    # add button for moving channels up

    move_down_button = Button(
        ntoolbar_frame, text=" " + chr(8595) + " ",
        command=lambda: move_channel(edit_listbox, "down")
    )
    # add buttons for moving channels down

    edit_listbox.bind("<Up>", lambda _: move_channel(edit_listbox, "up"))
    edit_listbox.bind("<Down>", lambda _: move_channel(edit_listbox, "down"))
    # bind the up and down arrow keys to move channels within the Listbox

    info_button = Button(
        ntoolbar_frame, text=" " + chr(128712) + " ",
        command=lambda: show_info(edit_listbox)
    )
    # create information button

    info_button.pack(side="left", padx=2, pady=2)
    move_up_button.pack(side="left", padx=(10, 2), pady=2)
    move_down_button.pack(side="left", padx=2, pady=2)
    ntitle_label.pack(pady=5)
    # place elements