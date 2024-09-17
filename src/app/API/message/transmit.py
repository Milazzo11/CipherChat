"""
Standard message transmission.

:author: Max Milazzo
"""


import random
from app.API.connection import transmit
from app.API.message.packets import SKEPacketEncoder
from app.util.channel import Channel


def send(
    tag: str, message_text: str, channel: Channel, webhooks: list,
    attachments: list = []
) -> None:
    """
    Send encrypted message to randomly chosen viable webhook.

    :param tag: the user (name) tag
    :param message_text: base message plaintext
    :param channel: application channel to send message to
    :param webhooks: list of viable webhooks where messages can be sent
    :param attachments: list of attachment objects associated with message
    """

    packet = SKEPacketEncoder(tag, message_text, channel.key, attachments)
    # initialize message packet encoder object

    header = packet.header(channel.name, channel.id)
    # generate message header
    
    webhook = random.choice(webhooks)
    # select random viable webhook

    attachment_files = [
        attachment.encode(channel.key) for attachment in attachments
    ]
    # generate encoded attachment files

    transmit.send(header, packet.encode(), webhook, attachment_files)
    # transmit header and encoded message packet data to selected webhook