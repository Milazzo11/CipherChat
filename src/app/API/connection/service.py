"""
Basic Discord message scanning service.

:author: Max Milazzo
"""


import time
from app.API.connection import fetch


PING_SPEED = 1
# delay (in seconds) between checks for new messages


FETCH_DELAY = 0
# delay between consecutive fetch requests within a ping cycle


kill_flag = False
# global flag that can be set to terminate the read loop.


def read_history(discord_cids: list, auth: dict) -> list:
    """
    Retrieves the message history for the specified Discord channels.

    :param discord_cids: Discord channel IDs to retrieve message history from
    :param auth: authorization headers for making requests to the Discord API

    :return: list of messages retrieved from the specified channels
    """
    
    history = []
    
    for channel_id in discord_cids:
        history.extend(fetch.get_messages(channel_id, auth))
        # add messages to chat history log

        time.sleep(FETCH_DELAY)
        
    return history


def read_loop(log: list, discord_cids: list, auth: dict, func: callable) -> None:
    """
    Monitors Discord channels for new messages, invoking a provided callable
    function on them when found.

    :param log: list to store previously seen messages
    :param discord_cids: Discord channel IDs to monitor
    :param auth: authorization headers for making requests to the Discord API
    :param func: a callable function that processes new messages
    """

    global kill_flag

    while True:
        if kill_flag:
            kill_flag = False
            return
            # halt scanning loop when global kill flag set to true

        new_msgs = []
        
        for discord_cid in discord_cids:
            fetch_num = 0
            
            while True:
                test_msgs = fetch.get_messages(
                    discord_cid, auth, fetch_num + 1
                )
                # fetch recent messages
                
                if len(test_msgs) <= fetch_num:
                    new_msgs.extend(test_msgs)
                    fetch_num = 0
                    break
                    # special case for if fewer messages found than the passed limit

                test_msg_id = test_msgs[fetch_num]["id"]
                # extract most recent fetched message ID
                
                if any(item["id"] == test_msg_id for item in log):
                    break
                    # break loop if most recent fetched message (matched by ID)
                    # has already been seen
                
                fetch_num += 1
                time.sleep(FETCH_DELAY)
                
            if fetch_num > 0:
                new_msgs.extend(test_msgs[:-1])
                # add newly fetched messages to new message list
                
        if len(new_msgs) > 0:
            halt_flag = func(new_msgs)
            # call function on messages (sorted by timestamp)

            if halt_flag:
                return
                # if message processing function returns a true halt flag, halt scanning

            log.extend(new_msgs)
            # add new messages to the message log
            
        time.sleep(PING_SPEED)