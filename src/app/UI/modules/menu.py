"""
Menu UI module.

:author: Max Milazzo
"""


from app.UI.components.delete import confirm_delete
from app.UI.components.edit import open_edit_window
from app.UI.components.invite import open_invite_window
from app.UI.components.join import open_join_window
from app.UI.components.new import open_new_channel_window
from tkinter import Event, Menu, Tk


def show_menu(event: Event, root: Tk) -> None:
    """
    Display UI option menu.

    :param event: click event
    :param root: UI root
    """

    menu = Menu(root, tearoff=0)
    # initialize menu

    menu.add_command(label="New", command=open_new_channel_window)
    menu.add_command(label="Edit", command=open_edit_window)
    menu.add_command(label="Join", command=open_join_window)
    menu.add_command(label="Invite", command=open_invite_window)
    menu.add_command(label="Leave", command=confirm_delete)
    # add menu commands
    
    menu.post(event.x_root, event.y_root)
    # display the menu at button click location