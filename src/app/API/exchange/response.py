"""
Key exchange invite (join response) API functions.

:author: Max Milazzo
"""


import random
from app.API.connection import service, transmit
from app.API.exchange.packets import AKEResponseDecoder, AKEResponseEncoder, RESPONSE_IDENT
from app.util.channel import Channel
from app.util.paths import ERROR_LOG_PATH


def join_func_factory(
    request_id: str, private_key: bytes, make_channel_func: callable
) -> callable:
    """
    Constructs complete channel join function.

    :param request_id: associated request identifier
    :param private_key: The private key used for decryption.
    :param make_channel_func: callback function defining custom channel
        creation actions

    :return: complete channel join function
    """

    def join_func(messages: list) -> bool:
        """
        Channel join function.

        :param messages: list of encrypted messages to be scanned
        :return: service read loop kill flag status (False)
        """

        for message in sorted(messages, key=lambda message: message["timestamp"]):
            try:
                if not message["content"].startswith(RESPONSE_IDENT):
                    continue
                    # skip message if it is not identified as an invite
                    
                decoder = AKEResponseDecoder(message["content"], private_key)
                # initialize response decoder object

                header = decoder.header()
                # extract packet header
                
                if header == request_id:
                # determine if selected invite is a valid response to
                # the corresponding join request

                    body = decoder.decode()
                    # extract packet body

                    make_channel_func(header, body)
                    # execute custom channel creation callback function

            except Exception as e:
                with open(ERROR_LOG_PATH, "a") as f:
                    f.write(
                        "[INVITE SCAN ERROR]\n" +
                        f'MESSAGE           : "{message["content"]}"\n' +
                        f'TIMESTAMP         : "{message["timestamp"]}"\n' +
                        f"(ERROR) {e}\n\n"
                    )
                    # log invite scan errors

        return False
        # do not halt if running within service read loop

    return join_func


def scan(discord_cids: list, auth: dict, join_func: callable) -> None:
    """
    Scans channels for valid invite (response to previous join request) and
    executes channel join callback function.

    :param discord_cids: Discord channel IDs to retrieve message history from
    :param auth: authorization headers for making requests to the Discord API
    :param join_func: callback function defining channel join action
    """
    
    history = service.read_history(discord_cids, auth)
    # fetch message history

    service.read_loop(history, discord_cids, auth, join_func)
    # scan new messages for valid invite

    
def send(request_id: str, tag: str, channel: Channel, public_key: bytes, webhooks: list) -> None:
    """
    Sends a channel invite (join response).

    :param request_id: associated request identifier
    :param tag: the user (name) tag
    :param channel: channel to send invote for
    :param public_key: the public key used for encryption
    :param webhooks: list of viable webhooks where messages can be sent
    """    
    
    response = AKEResponseEncoder(request_id, tag, channel, public_key)
    # initialize response object
    
    webhook = random.choice(webhooks)
    # select random viable webhook
    
    transmit.send(response.header(), response.encode(), webhook)
    # transmit channel invite (join response)