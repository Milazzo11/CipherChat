"""
Channel file password encryption and decryption.

:author: Max Milazzo
"""


import os
import pickle
from app.crypto.symmetric import LKE, KEY_SIZE, BLOCK_SIZE, BYTE_SIZE
from app.lock.setup import make_pwd
from app.util import display
from app.util.paths import CHANNELS_PATH, ENCRYPTED_CHANNELS_PATH, ERROR_LOG_PATH
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from getpass import getpass


N = 65536
# Scrypt CPU and memory cost parameter (2^16)

R = 8
# Scrypt lock size parameter

P = 1
# Scrypt parallelization parameter


SALT = b"0" * 16
# Scrypt salt constant


IV = b"0" * (BLOCK_SIZE // BYTE_SIZE)
# key IV constant


cipher = None
# global channel file encryption cipher


def set_key(password: str) -> None:
    """
    Derives and sets the key in global cipher from password input.

    :param password: entered password
    """
    
    global cipher
    
    kdf = Scrypt(salt=SALT, length=KEY_SIZE // BYTE_SIZE, n=N, r=R, p=P)
    cipher = LKE(key=kdf.derive(password.encode()), iv=IV)
    # use Scrypt algorithm to derive and set key in global cipher


def encrypt(static: bool) -> None:
    """
    Encrypts channel data file.

    :param static: specifies whether channel data is unchanging or has been
        possibly altered via UI interaction during the lifetime of the program
    """

    if static:
        with open(CHANNELS_PATH, "rb") as f:
            unencrypted_data = f.read()
            # load unencrypted data directly from channels file

    else:
        from app.UI.modules import main
        # import main module

        unencrypted_data = pickle.dumps(main.channels)
        # load unencrypted data from main module channels

    if cipher is not None:
        encrypted_data = cipher.encrypt(unencrypted_data, byte_output=True)
        # encrypt data

        os.remove(CHANNELS_PATH)
        # remove unencrypted channel data file

        with open(ENCRYPTED_CHANNELS_PATH, "wb") as f:
            f.write(encrypted_data)
            # write to encrypted data file

        if os.path.exists(ERROR_LOG_PATH):
            os.remove(ERROR_LOG_PATH)
            # remove error log file
            # (error information can potentially be used in an attack to uncover hidden keys)


def decrypt() -> None:
    """
    Decrypts channel data file.
    """

    with open(ENCRYPTED_CHANNELS_PATH, "rb") as f:
        encrypted_data = f.read()
        # load encrypted data

    while True:
        pwd = getpass()
        set_key(pwd)
        # set cipher key using provided password

        try:
            decrypted_data = cipher.decrypt(encrypted_data, byte_output=True)
            pickle.loads(decrypted_data)
            # attempt to decrypt and load channel pickle data

            break
            # if data can be decrypted and loaded, password accepted

        except:
            display.clear()
            print("Error: Incorrect password")
            print("Try again\n")
            # if data cannot be decrypted and loaded, password rejected

    os.remove(ENCRYPTED_CHANNELS_PATH)
    # remove encrypted data file

    with open(CHANNELS_PATH, "wb") as f:
        f.write(decrypted_data)
        # write to unencrypted data file


def startup(static: bool) -> None:
    """
    Handles application startup functionality.

    :param static: specifies whether channel data is unchanging or has been
        possibly altered via UI interaction during the lifetime of the program
    """
    
    if os.path.exists(ENCRYPTED_CHANNELS_PATH):
        print("Welcome back to CipherChat!\n")
        decrypt()
        # decrypt channel data file

    elif not static:
        print("Welcome to CipherChat!")
        print("Please enter a secure password to get started\n")
        make_pwd()
        # create a password for encryption if one is not currently set

    display.clear()