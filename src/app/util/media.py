"""
Message media processing.

:author: Max Milazzo
"""


import io
import os
import requests
from app.crypto.symmetric import SKE
from discord import File


ATTACHMENT_IDENT = "<attachment>"
# oversized symmetric key encrypted message (with file attachment) identifier


class Attachment:
    """
    Message attachment object.
    """

    @staticmethod
    def message_handler(message: dict) -> None:
        """
        Handles oversized messages that use an attachment to transmit data.

        :param message: message data dictionary
        """

        if message["content"] == ATTACHMENT_IDENT:
            file_url = message["attachments"][0]["url"]
            file_request = requests.get(file_url)
            message["content"] = file_request.content.decode("utf-8")
            # extract oversized message content from data file attachment

            message["attachments"][0] = None
            # remove data file from message attachments while flagging its
            # previous location in the list


    @staticmethod
    def get_bytes(message: dict, attachment_index: int) -> bytes:
        """
        Extracts file bytes from an attachment.

        :param message: message data dictionary
        :param attachment_index: index of attachment

        :return: file bytes
        """

        file_url = message["attachments"][attachment_index]["url"]
        file_request = requests.get(file_url)
        file_bytes = file_request.content
        # extract file bytes

        return file_bytes


    @staticmethod
    def name_encode(filename: str) -> str:
        """
        Converts unencoded filename to encoded filename.

        :param filename: unencoded filename
        :return: encoded filename
        """

        return filename + ".enc"
    

    @staticmethod
    def name_decode(filename: str) -> str:
        """
        Converts encoded filename to unencoded filename.

        :param filename: encoded filename
        :return: unencoded filename
        """

        return filename.rsplit(".", 1)[0]
    

    def __init__(self, file_bytes: bytes, path: str = None, iv: bytes = None) -> None:
        """
        Message attachment object initialization.

        :param file_bytes: attachment file bytes
        :param path: attachment file path
        :param iv: attachment encryption/decryption IV
        """

        self._bytes = file_bytes
        # set attachment bytes

        if path is not None:
            self.path = path
            self.filename = os.path.basename(path)
            # extract filename from path

        if iv is None:
            self.iv = SKE.iv()
            # generate random IV if none set

        else:
            self.iv = iv
            # set IV value if passed


    def encode(self, key: bytes) -> File:
        """
        Encodes attachment data for transmission.

        :param key: symmetric encryption key
        :return: Discord file object with encrypted data bytes
        """

        cipher = SKE(key=key, iv=self.iv)
        encrypted_data = cipher.encrypt(self._bytes, byte_output=True)
        # encrypt file data

        return File(
            io.BytesIO(encrypted_data),
            filename=Attachment.name_encode(self.filename)
        )
    

    def decode(self, key: bytes) -> bytes:
        """
        Decodes attachment data.

        :param key: symmetric encryption key
        :return: decrypted file bytes
        """

        cipher = SKE(key=key, iv=self.iv)
        return cipher.decrypt(self._bytes, byte_output=True)