"""
Basic Discord message post transmission.

:author: Max Milazzo
"""


import io
from app.util.media import ATTACHMENT_IDENT
from discord import File, SyncWebhook


TEXT_LIMIT = 2000
# standard-sized transmission character limit


def send(ident: str, text: str, webhook: SyncWebhook, attachment_files: list = []) -> None:
    """
    Sends messages via webhook to Discord channel.

    :param ident: message identifier
    :param text: message body text
    :param webhook: the webhook where the message is being sent
    :param attachment_files: list of loaded encrypted attachment files
    """

    transmission = ident + "\n" + text
    # construct transmission text

    if len(transmission) > TEXT_LIMIT:
        attachment_files.insert(0,
            File(
                io.BytesIO(transmission.encode("utf-8")),
                filename="data.txt"
            )
        )
        # set message data attachment file as primary (first) attachment file

        transmission = ATTACHMENT_IDENT
        # set message content to oversized transmission identification

    webhook.send(transmission, files=attachment_files)
    # send transmission