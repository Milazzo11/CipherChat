"""
Key exchange join request API functions.

:author: Max Milazzo
"""


import random
import threading
import time
import uuid
from app.API.connection import service, transmit
from app.API.exchange import response
from app.API.exchange.packets import AKERequestDecoder, AKERequestEncoder, REQUEST_IDENT
from app.crypto.asymmetric import AKE
from app.util.paths import ERROR_LOG_PATH
from datetime import datetime


REQUEST_EXPIRE = 600
# request timestamp expiry time limit (seconds)


def scan(discord_cids: list, auth: dict) -> dict:
    """
    Scans channels and fetches join requests.

    :param discord_cids: Discord channel IDs to retrieve message history from
    :param auth: authorization headers for making requests to the Discord API

    :return: active join requests
    """
    
    messages = service.read_history(discord_cids, auth)
    # fetch message history

    requests = {}

    for message in messages:
        if not message["content"].startswith(REQUEST_IDENT):
            continue
            # skip message if it isn't identified as a request
        
        server_timestamp = datetime.fromisoformat(message["timestamp"])
        time_diff = time.time() - server_timestamp.timestamp()
        # calculate request time offset
        
        if time_diff > REQUEST_EXPIRE:
            continue
            # skip message if request is expired
        
        try:
            decoder = AKERequestDecoder(message["content"])
            # initialize decoder

            header = decoder.header()
            # extract header
            
            requests[header] = decoder.decode()
            requests[header]["timestamp"] = server_timestamp
            # store decoded request data 
            
        except Exception as e:
            with open(ERROR_LOG_PATH, "a") as f:
                f.write(
                    "[REQUEST SCAN ERROR]\n" +
                    f'MESSAGE           : "{message["content"]}"\n' +
                    f'TIMESTAMP         : "{message["timestamp"]}"\n' +
                    f"(ERROR) {e}\n\n"
                )
                # log request scan errors
            
    return requests

    
def send(
    tag: str, message: str, discord_cids: list, auth: dict, webhooks: list,
    make_channel_func: callable
) -> None:
    """
    Sends a channel join request.
    
    :param tag: the user (name) tag
    :param message: message data to send
    :param discord_cids: Discord channel IDs to retrieve message history from
    :param auth: authorization headers for making requests to the Discord API
    :param webhooks: list of viable webhooks where messages can be sent
    :param make_channel_func: callback function defining custom channel
        creation actions
    """
    
    cipher = AKE()
    # create cipher

    request = AKERequestEncoder(tag, message, cipher.public_key)
    # initialize request object
    
    request_id = str(uuid.uuid4())
    # generate unique request tag
    
    join_func = response.join_func_factory(
        request_id, cipher.private_key, make_channel_func
    )
    # generate complete channel join function
    
    invite_scan_thread = threading.Thread(
        target=response.scan, args=(discord_cids, auth, join_func),
        daemon=True
    )
    invite_scan_thread.start()
    # start parallel invite scan thread

    webhook = random.choice(webhooks)
    # select random viable webhook
    
    header = request.header(request_id)
    transmit.send(header, request.encode(), webhook)
    # transmit channel join request