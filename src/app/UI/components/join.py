"""
Channel join request UI component.

:author: Max Milazzo
"""


from app.API.connection import service
from app.API.exchange import request
from app.UI.components.new import open_new_channel_window
from app.UI.modules import main
from app.util.channel import Channel
from tkinter import Button, Label, messagebox, Text, Toplevel, ttk


def on_close(join_window: Toplevel) -> None:
    """
    Activate service kill flag and destroy join window.

    :param join_window: join window
    """

    service.kill_flag = True
    join_window.destroy()


def make_channel_func_factory(
    join_window: Toplevel, open_new_channel_window: callable
) -> callable:
    """
    Channel invite creator function factory.

    :param join_window: join window
    :param open_new_channel_window: open new channel window function

    :return: channel creator function
    """

    def make_channel_func(_, body: dict) -> bool:
        """
        Channel invite creator function.

        :param body: channel invitation packet body
        :return: channel creation status
        """

        res = messagebox.askquestion(
            "Channel Invite",
            f'Invite from {body["tag"]} to join channel "{body["channel"]["name"]}"\n(ID: {body["channel"]["id"]})\n\nWould you like to accept?'
        )

        if res == "yes":
            join_window.destroy()
            open_new_channel_window(Channel(data_dict=body["channel"]))
            return True
            # create new channel from invite

        else:
            return False
            # decline invite

    return make_channel_func


def send_join_request(
    join_window: Toplevel, ntitle_label: Label, ntoolbar_frame: ttk.Frame,
    req_msg_input: Text
) -> None:
    """
    Sends a join request to the server.

    :param join_window: join window
    :param ntitle_label: main title label
    :param ntoolbar_frame: main toolbar frame
    :param req_msg_input: request message input
    """

    req_msg = req_msg_input.get("1.0", "end-1c").rstrip()
    # get request message

    ntitle_label.config(text="Request Pending...")
    ntoolbar_frame.pack_forget()
    req_msg_input.pack_forget()
    join_window.geometry("250x30")
    # configure join window

    make_channel_func = make_channel_func_factory(
        join_window, open_new_channel_window
    )
    # generate channel invite creator function

    request.send(
        main.user_config["tag"], req_msg, main.server_config["channels"],
        main.user_config["auth"], main.server_config["webhooks"],
        make_channel_func
    )
    # send request to server

    join_window.protocol("WM_DELETE_WINDOW", lambda: on_close(join_window))
    # specify custom on_close logic


def open_join_window():
    """
    Opens the channel join window.
    """

    x, y = main.root.winfo_pointerxy()

    join_window = Toplevel(main.root)
    join_window.attributes("-topmost", True)
    join_window.title("Join Request")
    # Create a new Toplevel window for joining a new channel by invite 

    ntitle_frame = ttk.Frame(join_window)
    ntoolbar_frame = ttk.Frame(join_window)

    join_window.geometry(f"250x120+{x}+{y}")
    # set geometry
    
    ntitle_label = Label(ntitle_frame, text="Request Message")
    # create main title label

    ntitle_frame.pack(side="top")
    ntoolbar_frame.pack(side="bottom", fill="x")

    req_msg_input = Text(join_window, height=5, width=35)
    req_msg_input.pack(side="top", fill="both", expand=True, padx=2)
    # create request message input

    nsend_button = Button(
        ntoolbar_frame, text="Send",
        command=lambda: send_join_request(
            join_window, ntitle_label, ntoolbar_frame, req_msg_input
        )
    )
    # create join request send button
    
    nclear_button = Button(
        ntoolbar_frame, text="Clear",
        command=lambda: req_msg_input.delete("1.0", "end-1c")
    )
    # create join request clear button

    nsend_button.pack(side="left", padx=2, pady=2)
    nclear_button.pack(side="left", padx=2, pady=2)
    ntitle_label.pack(pady=5)
    # place elements