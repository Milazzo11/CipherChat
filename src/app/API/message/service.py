"""
Standard message receipt service.

:author: Max Milazzo
"""


from app.API.connection import service
from app.API.message.packets import SKEPacketDecoder, SKE_IDENT
from app.util.channel import Channel
from app.util.media import Attachment
from app.util.paths import ERROR_LOG_PATH
from datetime import datetime, timezone
from typing import Union


TIMESTAMP_SHIFT_MAX = 60
# defines the maximum allowed timestamp shift between server and client timestamps


seen_ivs = []
# global list of previously seen message IV values used to perform IV authentication


def parse(
    plaintext: str, message: dict, channel: Channel,
    server_timestamp: datetime, process_func: Union[callable, None]
) -> None:
    """
    Parses, validates, and processes the received message.

    :param plaintext: the decrypted plaintext
    :param message: Discord message data dictionary
    :param channel: channel to process messages from
    :param server_timestamp: message timestamp from Discord server
    :param process_func: decrypted message custom process callback function
    """

    global seen_ivs
    
    epoch_server_timestamp = server_timestamp.timestamp()
    message_iv, message_timestamp, message_plaintext = plaintext.split(" ", 2)
    # parse plaintext message information

    if message_iv in seen_ivs:
        raise Exception("Repeat encoding IV encountered")
        # detect repeat message IV
        
    seen_ivs.append(message_iv)
    # add message IV to global list

    message_timestamp = float(message_timestamp)
    time_diff = abs(epoch_server_timestamp - message_timestamp)
    # calculate server and client message timestamp shift 

    if time_diff > TIMESTAMP_SHIFT_MAX:
        raise Exception(
            f"Timestamp validation failure: {time_diff}s " +
            f"discrepency exceeds limit of {TIMESTAMP_SHIFT_MAX}s"
        )
        # detect timestamp validation error
    
    if process_func is None:
        print(f"[{server_timestamp}]\n{message_plaintext}\n", flush=True)
        # display timestamped messages by default

        for index, attachment in enumerate(message["attachments"]):
        # enumerate through message attachments to display relevant data

            if attachment is None:
                continue
                # skip "None" flagged attachment indices
            
            filename = Attachment.name_decode(attachment["filename"])
            # extract attachment filename

            download_code = f"{channel.id}/{message['channel_id']}/{message['id']}.{index}"
            # generate attachment download code

            print(f'<attachment "{filename}">\n{download_code}\n', flush=True)
            # display attachment data
    
    else:
        process_func(message_plaintext, message, channel, server_timestamp)
        # process message with callback function otherwise


def process(messages: list, channel: Channel, process_func: Union[callable, None]) -> bool:
    """
    Decrypts and processes messages.

    :param messages: list of encrypted messages to be processed
    :param channel: channel to process messages from
    :param process_func: decrypted message custom process callback function

    :return: service read loop kill flag status (False)
    """

    for message in sorted(messages, key=lambda message: message["timestamp"]):
    # loop through messages sorted by timestamp

        ciphertext = "N/A"
        server_timestamp = "N/A"
        # default ciphertext and server timestamp strings used in error messages

        try:
            Attachment.message_handler(message)
            # handle and proprly format oversized messages with attachment data

            if not message["content"].startswith(SKE_IDENT):
                continue
                # skip non-symmetric key encrypted messages
        
            server_timestamp = datetime.fromisoformat(message["timestamp"])
            # parse server timestamp
            
            decoder = SKEPacketDecoder(message["content"], channel.key)
            # initialize message packet decoder object

            if decoder.header() == channel.id:
                plaintext = decoder.decode()
                # decode message if it belongs to the correct channel

                ciphertext = decoder.body
                # store ciphertext value for possible use in error message

                parse(plaintext, message, channel, server_timestamp, process_func)
                # parse, validate, and process message
                
        except Exception as e:
            with open(ERROR_LOG_PATH, "a") as f:
                f.write(
                    "[MESSAGE DISPLAY ERROR]\n" +
                    f'MESSAGE CHANNEL   : "{channel.name}"\n' +
                    f'ENCRYPTED TEXT    : "{ciphertext}"\n' +
                    f"SERVICE TIMESTAMP : [{datetime.now(tz=timezone.utc)}]\n" + 
                    f"SERVER TIMESTAMP  : [{server_timestamp}]\n" +
                    f"(ERROR) {e}\n\n"
                )
                # log message display errors

    return False
    # do not halt if running within service read loop


def start(
    channel: Channel, discord_cids: list, auth: dict,
    process_func: Union[callable, None] = None
) -> None:
    """
    Start the message receipt service.

    :param channel: channel to display messages from
    :param discord_cids: Discord channel IDs to fetch messages from
    :param auth: authorization headers for making requests to the Discord API
    :param process_func: decrypted message custom process callback function
    """
    
    if process_func is None:
    # display message channel header if custom processing not set

        title = "CHANNEL: " + channel.name
        # set channel display title

        print("=" * (len(title) + 2), flush=True)
        print(title + " |", flush=True)
        print("_" * (len(title) + 1) + "|\n", flush=True)
        # display channel header text
    
    history = service.read_history(discord_cids, auth)
    process(history, channel, process_func)
    # display past messages in channel
    
    service.read_loop(
        history, discord_cids, auth,
        lambda messages: process(messages, channel, process_func)
    )
    # start service read loop to scan for new message to decode and display