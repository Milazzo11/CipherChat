"""
Channel invite UI component.

:author: Max Milazzo
"""


from app.API.exchange import request, response
from app.UI.modules import main
from app.util.channel import channel_search
from datetime import datetime, timedelta, timezone
from tkinter import Button, END, Label, Listbox, messagebox, Scrollbar, Toplevel, ttk
from typing import Union


inv_open_ready = True
# True when invite window is ready to be opened


def show_invite_popup(invite_listbox: Listbox, items_map: dict) -> None:
    """
    Displays invitation creation popup.

    :param invite_listbox: join request (invite) listbox
    :param item_map: join request key item map
    """
    
    global inv_open_ready

    if not inv_open_ready:
        return

    inv_open_ready = False

    selected_index = invite_listbox.curselection()
    # get selected index
    
    if selected_index:
        selected_item = items_map[invite_listbox.get(selected_index)]
        inv_channel_name = main.clicked.get()
        # get selected items

        if selected_item[1]["msg"] == "":
            msg_text = ""
        else:
            msg_text = f'\n\nMessage: {selected_item[1]["msg"]}'

        res = messagebox.askquestion(
            "Invitation Confirmation", 
            f'Confirm invitation of user "{selected_item[1]["tag"]}" to channel "{inv_channel_name}"\n\n' +
            f'Request ID: {selected_item[0]}' + msg_text
        )
        # show confirmation window

        if res == "yes":
            inv_channel = channel_search(main.channels, inv_channel_name)
            # find join requested channel
            
            response.send(
                selected_item[0], main.user_config["tag"], inv_channel,
                selected_item[1]["key"], main.server_config["webhooks"]
            )
            # send invite (response to join request)

            messagebox.showinfo("Invitation Sent", "Channel invite sent.")
            
    inv_open_ready = True


def reload_invite_window(invite_window: Toplevel) -> None:
    """
    Reloads the channel invite window.
    """
    
    x = invite_window.winfo_x()
    y = invite_window.winfo_y()

    invite_window.destroy()
    open_invite_window((x, y))


def open_invite_window(pos: Union[tuple, None] = None) -> None:
    """
    Opens the channel invite window.

    :param pos: position of the window
    """

    if len(main.channels) == 0:
        return
        # return when no channels present

    join_requests = request.scan(
        main.server_config["channels"], main.user_config["auth"]
    )
    # get join requests
    
    if pos is None:
        x, y = main.root.winfo_pointerxy()
    else:
        x, y = pos

    invite_window = Toplevel(main.root)
    invite_window.attributes("-topmost", True)
    invite_window.title("Channel Invite")
    # create a new Toplevel window for inviting to channels

    ntitle_frame = ttk.Frame(invite_window)
    ntoolbar_frame = ttk.Frame(invite_window)
    
    invite_window.geometry(f"250x130+{x}+{y}")
    # set geometry

    ntitle_label = Label(ntitle_frame, text="Active Requests:")
    # create main title label

    ntitle_frame.pack(side="top")
    ntoolbar_frame.pack(side="bottom", fill="x")

    invite_listbox = Listbox(invite_window, height=5, width=35, font=("Courier New", 8))
    invite_listbox.pack(side="left", fill="both", expand=True, padx=2, pady=(0, 2))
    # create invitations ListBox
    
    scrollbar = Scrollbar(invite_window, command=invite_listbox.yview)
    scrollbar.pack(side="right", fill="y")
    invite_listbox.config(yscrollcommand=scrollbar.set)
    # put ListBox in Scrollbar
    
    items_list = []
    items_map = {}
    max_tag_length = 0
    
    if len(join_requests) > 0:
        max_tag_length = max(len(join_requests[key]["tag"]) for key in join_requests)
        # calculate maximum join request tag length

    for key in join_requests:
        timestamp_str = join_requests[key]["timestamp"].strftime("%H:%M:%S, %d/%m/%Y")
        padding_spaces = " " * (5 + max_tag_length - len(join_requests[key]["tag"]))
        # calculate display spacing
        
        padded_key = (
            join_requests[key]["tag"] + padding_spaces + timestamp_str +
            (" " * 10) + key
        )
        items_list.append((join_requests[key]["timestamp"], padded_key))
        items_map[padded_key] = (key, join_requests[key])
        # add formatted items to key map

    for item in sorted(items_list, reverse=True):
        invite_listbox.insert(END, item[1])
        # inster items into ListBox
    
    invite_listbox.bind(
        "<Double-Button-1>",
        lambda _: show_invite_popup(invite_listbox, items_map)
    )
    # bind the double click event to show the invitation popup

    reload_button = Button(
        ntoolbar_frame, text=" " + chr(10227) + " ",
        command=lambda: reload_invite_window(invite_window)
    )
    # add reload option (on reload, any new join requests will show)
    
    cur_time = datetime.now(timezone.utc)
    expire_time = cur_time - timedelta(seconds=request.REQUEST_EXPIRE)
    # calculate join request expiration time
    
    info = Label(
        ntoolbar_frame,
        text=f"[ {expire_time.strftime('%H:%M:%S')} - {cur_time.strftime('%H:%M:%S')} ]"
    )
    # place join request time info into a label

    reload_button.pack(side="left", padx=2, pady=2)
    info.pack(side="left", padx=2, pady=2)
    ntitle_label.pack(pady=5)
    # place elements