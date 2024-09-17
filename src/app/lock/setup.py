"""
Channel file encryption setup.

:author: Max Milazzo
"""


from app.lock import lock
from app.util import display
from getpass import getpass


def make_pwd() -> None:
    """
    Create a new password for encryption.
    """
    
    while True:
        pwd = getpass()
        # get password
        
        print("\nConfirm password")
        pwd_confirm = getpass()
        # confirm password
        
        if pwd == pwd_confirm:
            break
            # passwords are the same, and confirmation successful

        else:
            display.clear()
            print("Error: passwords do not match")
            print("Try again\n")
            # passwords are not the same, and confirmation failed

    lock.set_key(pwd)
    # set the lock global cipher key using new password