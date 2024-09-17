"""
Discord message fetch requests.

:author: Max Milazzo
"""


import json
import requests


FETCH_URL = "https://discord.com/api/v9/channels/{channel_id}/messages?limit={limit}"
# Discord message fetch API URL


FETCH_MAX = 100
# message fetch maximum count


def get_messages(channel_id: str, auth: dict, limit: int = FETCH_MAX) -> list:
    """
    Fetches messages from a Discord channel.

    :param channel_id: Discord channel ID
    :param auth: authorization headers for making requests to the Discord API
    :param limit: message fetch limit

    :return: fetched message data
    """

    res = requests.get(
        FETCH_URL.format(channel_id=channel_id, limit=limit),
        headers=auth
    )
    # make Discord API request

    return json.loads(res.text)
    # format and return response data