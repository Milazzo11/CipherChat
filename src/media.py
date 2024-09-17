"""
Standard CipherChat media extraction tool.

:author: Max Milazzo
"""


from app.API.connection import fetch
from app.API.message.packets import SKEPacketDecoder
from app.util import display
from app.util import config
from app.util.media import Attachment
from run import startup
from tkinter import filedialog


def file_save(filename: str, file_bytes: bytes) -> None:
    """
    Save extracted file.

    :param filename: extracted filename
    :param file_bytes: extracted and decrypted file bytes
    """

    f = filedialog.asksaveasfile(mode="wb", initialfile=filename)
    # open file save dialog

    if f is None:
        return
        # exit if dialog closed with "cancel"

    f.write(file_bytes)
    f.close()
    # save file data


def main() -> None:
    """
    Main program entry point.
    """

    print("CipherChat Media Manager\n")
    print("Enter attachment download code:")

    code = input("> ")
    # get attachment download code

    try:
        channel_id, discord_cid, attachment_id = code.split("/")
        message_id, attachment_index = attachment_id.split(".")
        attachment_index = int(attachment_index)
        # parse attachment download code

        channels = config.channels_load()
        selected_channel = next((c for c in channels if c.id == channel_id), None)
        # fetch selected channel data specified in attachment download code

        if selected_channel is None:
            display.clear()
            print("Error: specified channel not found")
            input()
            return
            # abort media extraction on channel not found error

        user_config = config.user_config_load()
        messages = fetch.get_messages(discord_cid, user_config["auth"])
        message = next((m for m in messages if m["id"] == message_id), None)
        # fetch selected message data specified in attachment download code

        if message is None:
            display.clear()
            print("Error: specified message not found")
            input()
            return
            # abort media extraction on message not found error
        
        Attachment.message_handler(message)
        # handle and proprly format oversized messages with attachment data

        encrypted_file_bytes = Attachment.get_bytes(message, attachment_index)
        # extract attachment bytes

        if message["attachments"][0] is None:
            message["attachments"].pop(0)
            attachment_index -= 1
            # adjust attachment index to handle oversized message formatting
        
        decoder = SKEPacketDecoder(message["content"], selected_channel.key)
        # initialize decoder to parse message packet and extract associated
        # attachment IV for decryption

        file = Attachment(
            encrypted_file_bytes, iv=decoder.attachment_ivs[attachment_index]
        )
        file_bytes = file.decode(selected_channel.key)
        # extract decrypted attachment file bytes

        filename = Attachment.name_decode(
            message["attachments"][attachment_index]["filename"]
        )
        # extract attachment filename

        file_save(filename, file_bytes)
        # save extracted file

    except Exception as e:
        display.clear()
        print("Error: an unexpected error occured")
        print(e)
        input()
        # abort media extraction on unexpected error
        

if __name__ == "__main__":
    startup(static=True)
    # initialize program startup

    main()