"""
Channel deletion UI component.

:author: Max Milazzo
"""


from app.UI.modules import main
from app.util.channel import channel_search
from tkinter import messagebox


def confirm_delete() -> None:
    """
    Confirms and handles the deletion of a selected channel.
    """
    
    cur_channel_name = main.clicked.get()
    # get selected channel name
    
    if cur_channel_name == "":
        return
        # return if no channel selected
    
    res = messagebox.askquestion(
        f"Channel Deletion Confirmation: {cur_channel_name}",  
        f'Are you sure you want to leave the "{cur_channel_name}" channel?\nThis action cannot be undone.'
    )
    # confirm deletion
    
    if res == "yes":
    # continue with deletion if confirmation successful
    
        cur_channel = channel_search(main.channels, cur_channel_name)
        main.channels.remove(cur_channel)
        # delete channel from data
            
        r_index = main.channel_drop["menu"].index(cur_channel_name)
        main.channel_drop["menu"].delete(r_index)
        # delete channel from UI dropdown
        
        if len(main.channels) > 0:
            main.clicked.set(main.channel_drop["menu"].entrycget(0, "label"))
            # change selected channel to first in dropdown list

        else:
            main.clicked.set("")
            # set selected channel to empty if all channels deleted