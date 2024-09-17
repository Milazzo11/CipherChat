"""
Key exchange join request and invite response packet encoders and decoders.

:author: Max Milazzo
"""


import base64
import pickle
from app.crypto.asymmetric import AKE
from app.util.channel import Channel


REQUEST_IDENT = "(join)"
# channel join request message identifying start text


RESPONSE_IDENT = "(invite)"
# channel invite message identifying start text


class AKERequestEncoder:
    """
    Asymmetric key encrypted request packet encoder object initialization.
    """

    def __init__(self, tag: str, message: str, public_key: bytes) -> None:
        """
        Initializes an AKERequestEncoder instance.

        :param tag: the user (name) tag
        :param message: the content of the message to be encoded
        :param public_key: the public key used for encryption
        """
        
        self.tag = base64.b64encode(bytes(tag, "utf-8")).decode("utf-8")
        self.message = base64.b64encode(bytes(message, "utf-8")).decode("utf-8")
        self.public_key = public_key.decode("utf-8")
        
        
    def header(self, id: str) -> str:
        """
        Generates a header for the encoded message.

        :param id: unique request identifier
        :return: the generated header string
        """
        
        return REQUEST_IDENT + " " + id
        
        
    def encode(self) -> str:
        """
        Builds and encodes the final message string to be sent.

        :return: encoded message string
        """
        
        return self.tag + " " + self.message + "\n" + self.public_key
        

class AKERequestDecoder:
    """
    Asymmetric key encrypted request packet decoder object initialization.
    """
    
    def __init__(self, packet: str) -> None:
        """
        Initializes an AKERequestDecoder instance.

        :param packet: the encoded message packet string
        """
        
        self.packet = packet
        self._parse()
        

    def _parse(self) -> None:
        """
        Parses the header and body of the packet.
        """
        
        self._header, self.body = self.packet.split("\n", 1)
    
    
    def header(self) -> str:
        """
        Parses the packet header to extract relevant identifying information.

        :return: relevant decoded packet header information
        """
        
        return self._header.rsplit(" ", 1)[1]
    
    
    def decode(self) -> dict:
        """
        Decodes the packet body to extract relevant information.

        :return: decoded packet body information as a dictionary
        """

        sender_info, public_key = self.body.split("\n", 1)
        tag, message = sender_info.split(" ", 1)
        # extract tag and message data

        return {
        
            "tag": base64.b64decode(tag).decode("utf-8"),
            "msg": base64.b64decode(message).decode("utf-8"),
            "key": bytes(public_key, "utf-8")
            
        }
        # return decoded message data dictionary


class AKEResponseEncoder:
    """
    Asymmetric key encrypted response packet encoder object initialization.
    """

    def __init__(self, id: str, tag: str, channel: Channel, public_key: bytes) -> None:
        """
        Initializes an AKEResponseEncoder instance.

        :param id: associated request identifier
        :param tag: the user (name) tag
        :param channel: the channel object to be encoded
        :param public_key: the public key used for encryption
        """
        
        self.id = id
        self.tag = base64.b64encode(bytes(tag, "utf-8")).decode("utf-8")
        # set ID and tag data
        
        self.channel = pickle.dumps(channel.__dict__)
        # set channel data
        
        cipher = AKE(public_key=public_key)
        self.channel = cipher.encrypt(self.channel)
        # encrypt channel data
        

    def header(self) -> str:
        """
        Generates a header for the encoded message.

        :return: the generated header string
        """
        
        return RESPONSE_IDENT + " " + self.id
        
        
    def encode(self) -> str:
        """
        Builds and encodes the final message string to be sent.

        :return: encoded message string
        """
        
        return self.tag + " " + self.channel
    
        
class AKEResponseDecoder:
    """
    Asymmetric key encrypted response packet decoder object initialization.
    """
    
    def __init__(self, packet: str, private_key: bytes) -> None:
        """
        Initializes an AKEResponseDecoder instance.

        :param packet: The encoded message packet string.
        :param private_key: The private key used for decryption.
        """
        
        self.packet = packet
        self.private_key = private_key
        self._parse()

        
    def _parse(self) -> None:
        """
        Parses the header and body of the packet.
        """
        
        self._header, self.body = self.packet.split("\n", 1)
    
    
    def header(self) -> str:
        """
        Parses the packet header to extract relevant identifying information.

        :return: relevant decoded packet header information
        """
        
        return self._header.rsplit(" ", 1)[1]
    
    
    def decode(self) -> dict:
        """
        Decodes the packet body to extract relevant information.

        :return: decoded packet body information as a dictionary
        """
        
        tag, channel_ciphertext = self.body.split(" ", 1)
        cipher = AKE(private_key=self.private_key)
        channel_bytes = cipher.decrypt(channel_ciphertext)
        # parse response packet to extract tag and channel byte data

        return {
        
            "tag": base64.b64decode(tag).decode("utf-8"),
            "channel": pickle.loads(channel_bytes)
            
        }
        # return decoded message data dictionary