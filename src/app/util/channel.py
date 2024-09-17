"""
Channel object definition.

:author: Max Milazzo
"""


import uuid
from app.crypto.symmetric import SKE
from typing import Union


class Channel:
    """
    Channel object.
    """

    def __init__(self, name: str = None, data_dict: dict = None) -> None:
        """
        Channel object initialization.

        :param name: channel name
        :param data_dict: channel dictionary to load data from
        """
        
        if data_dict is None:
            self.name = name
            self.id = str(uuid.uuid4())     
            self.key = SKE.key()
            # set channel name and generate ID and key

        else:
            self.name = data_dict["name"]
            self.id = data_dict["id"]
            self.key = data_dict["key"]
            # load data from data dictionary


    def __str__(self) -> str:
        """
        Channel string representation.

        :return: string representation
        """
        
        return self.name
    

def channel_search(channels: list, search_name: str) -> Union[Channel, None]:
    """
    Search within a list of channel objects by name.

    :param channels: channel list
    :param search_name: channel name to search for

    :return: searched channel or None if not found
    """

    return next((c for c in channels if c.name == search_name), None)