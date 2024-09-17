"""
Symmetric key encryption packet encoder and decoders.

:author: Max Milazzo
"""


import base64
import time
from app.crypto.symmetric import SKE


SKE_IDENT = "["
# symmetric key encrypted message identifying start symbol


class SKEPacketEncoder:
    """
    Symmetric key encrypted message packet encoder object initialization.
    """

    def __init__(self, tag: str, message: str, key: bytes, attachments: list = []) -> None:
        """
        Initializes an SKEPacketEncoder instance.

        :param tag: the user (name) tag
        :param message: the content of the message to be encoded
        :param key: the cipher (channel) key used for encryption
        :param attachments: list of attachment objects associated with message
        """
        
        self.tag = tag
        self.message = message
        self.cipher = SKE(key=key)
        self.attachments = attachments

 
    def header(self, name: str, id: str) -> str:
        """
        Generates a header for the encoded message.

        :param name: the application channel name associated with the message
        :param id: The channel ID associated with the message.

        :return: the generated header string
        """
        
        return SKE_IDENT + name + "] " + id
 
 
    def encode(self) -> str:
        """
        Builds and encodes the final message string to be sent.

        :return: encoded message string
        """
        
        plaintext = str(time.time()) + " " + self.tag + ": " + self.message
        # set plaintext to include timestamp, tag, and message body
        
        packet_text = (
            base64.b64encode(self.cipher.iv).decode("utf-8") + " " +
            self.cipher.encrypt(plaintext)
        )
        # generate the base packet message, with the cipher's IV and encrypted
        # message (base64 encoded) with a space as the delimeter

        if len(self.attachments) > 0:
            packet_text += "\n"
            packet_text += " ".join(
                base64.b64encode(a.iv).decode("utf-8")
                for a in self.attachments
            )
            # include attached file IV values (if needed)

        return packet_text
    
    
class SKEPacketDecoder:
    """
    Symmetric key encrypted message packet decoder object initialization.
    """

    def __init__(self, packet: str, key: bytes) -> None:
        """
        Initializes an SKEPacketDecoder instance.

        :param packet: the encoded message packet string
        :param key: the cipher (channel) key used for decryption
        """
        
        self.packet = packet
        self.key = key

        self._parse()
        # parse packet upon initialization


    def _parse(self) -> None:
        """
        Parses the header and body of the packet.
        """
        
        self._header, self.body = self.packet.split("\n", 1)

        data_split = self.body.rsplit("\n", 1)
        self.body = data_split[0]
        # extract message body to exclude possible attachment IVs

        if len(data_split) > 1:
            encoded_attachment_ivs = data_split[1].split()
            # extract base64 encoded attachment IVs to list if present

            self.attachment_ivs = [
                base64.b64decode(iv) for iv in encoded_attachment_ivs
            ]
            # decode and store attachment IVs
    
    
    def header(self) -> str:
        """
        Parses the packet header to extract relavent identifying information.

        :return: relavent decoded packet header information
        """

        return self._header.rsplit(" ", 1)[1]
    
    
    def decode(self) -> str:
        """
        Decodes the packet body to extract relavent information.

        :return: decoded packet body information
        """

        iv, self.body = self.body.split(" ", 1)
        cipher = SKE(key=self.key, iv=base64.b64decode(iv))
        # initialize cipher using key and message IV
        
        return iv + " " + cipher.decrypt(self.body)
        # return base64 encoded IV text and decoded message (body) text