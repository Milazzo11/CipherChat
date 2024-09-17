"""
CipherChat help menu options.

:author: Max Milazzo
"""


import os
import shutil
from app.lock import lock, setup
from app.util import display
from app.util.paths import (
    ACTIVE_PROFILE_FLAG_FILENAME, DATA_DIR, ENCRYPTED_CHANNELS_FILENAME,
    ENCRYPTED_CHANNELS_PATH, PROFILE_IDENTIFIER_PATH, PROFILES_DIR,
    SERVER_CONFIG_FILENAME, SERVER_CONFIG_PATH, USER_CONFIG_FILENAME,
    USER_CONFIG_PATH
)


def app_credits() -> None:
    """
    Application credits and information display.
    """
    
    print("Discord CipherChat")
    print("© Maximus Milazzo\n")
    print("The CipherChat application strives to provide secure, easy, and anonymous group communication.")
    print('See the "README.txt" file for more information and to learn how it works.  Enjoy!')
    
    input()


def deactivate_profile() -> None:
    """
    Moves data from the currently active profile back into its archive folder.
    """

    with open(PROFILE_IDENTIFIER_PATH, "r") as f:
        current_profile = f.read()
        # get current profile name

    if os.path.exists(ENCRYPTED_CHANNELS_PATH):
        shutil.move(
            ENCRYPTED_CHANNELS_PATH,
            os.path.join(
                os.path.join(PROFILES_DIR, current_profile),
                ENCRYPTED_CHANNELS_FILENAME
            )
        )
        # save channel data (if it exists)

    shutil.move(
        USER_CONFIG_PATH,
        os.path.join(
            os.path.join(PROFILES_DIR, current_profile),
            USER_CONFIG_FILENAME
        )
    )
    # save user configuration file

    shutil.move(
        SERVER_CONFIG_PATH,
        os.path.join(
            os.path.join(PROFILES_DIR, current_profile),
            SERVER_CONFIG_FILENAME
        )
    )
    # save server configuration file

    os.remove(
        os.path.join(
            os.path.join(PROFILES_DIR, current_profile),
            ACTIVE_PROFILE_FLAG_FILENAME
        )
    )
    # remove active flag from profile


def activate_profile(selected_profile: str) -> None:
    """
    Activates the selected profile.
    
    :param selected_profile: selected profile name
    """

    with open(PROFILE_IDENTIFIER_PATH, "w") as f:
        f.write(selected_profile)
        # set selected profile in profile identifier file

    profile_channels_path = os.path.join(
        os.path.join(PROFILES_DIR, selected_profile),
        ENCRYPTED_CHANNELS_FILENAME
    )
    # construct profile channel data path

    if os.path.exists(profile_channels_path):
        shutil.move(
            os.path.join(
                os.path.join(PROFILES_DIR, selected_profile),
                ENCRYPTED_CHANNELS_FILENAME
            ),
            ENCRYPTED_CHANNELS_PATH  
        )
        # load profile channel data path (if it exists)

    shutil.move(
        os.path.join(
            os.path.join(PROFILES_DIR, selected_profile),
            USER_CONFIG_FILENAME
        ),
        USER_CONFIG_PATH
    )
    # load user configuration file

    shutil.move(
        os.path.join(
            os.path.join(PROFILES_DIR, selected_profile),
            SERVER_CONFIG_FILENAME
        ),
        SERVER_CONFIG_PATH
    )
    # load server configuration file
    
    with open(
        os.path.join(
            os.path.join(PROFILES_DIR, selected_profile),
            ACTIVE_PROFILE_FLAG_FILENAME
        ), "w"
    ) as f:
        f.write("THIS PROFILE IS CURRENTLY SET AS ACTIVE")
        # add active flag to profile
    
    
def profile_select() -> None:
    """
    Application configuartion and channel profile selection.
    """

    profiles = os.listdir(PROFILES_DIR)
    # get profiles list

    print("Choose profile to activate:\n")

    for index, profile in enumerate(profiles):
        print(index + 1, "-", profile)
        # display selection options

    option = input("\n> ")
    display.clear()

    try:
        selected_profile = profiles[int(option) - 1]
        # get profile selection
        
    except:
        print("Error: Invalid selection")
        print("Profile selection aborted")
        input()
        # handle profile selection error
        
        return

    try:
        deactivate_profile()
        # deactivates current active profile

    except:
        print("Error: Failed to deactivate current profile")
        print("Manual correction required")
        input()
        # handle profile deactivation error
        
        return

    try:
        activate_profile(selected_profile)
        # activates selected profile

    except Exception as e:
        print("Error: Failed to activate new profile")
        print("Manual correction required")
        input()
        # handle profile activation error
        
        return

    print(f'Profile "{selected_profile}" successfully activated')
    input()
    
    
def pwd_reset() -> None:
    """
    Application password reset utility.
    """

    if not os.path.exists(ENCRYPTED_CHANNELS_PATH):
        print("No password is currently set")
        input()
        return
        # detect if no password is currently set (application not used yet)

    print("Enter current password\n")
    lock.decrypt()
    display.clear()
    # decrypt channel data

    print("Enter new password\n")
    setup.make_pwd()
    display.clear()
    # generate new password

    lock.encrypt()
    print("Password reset")
    input()
    # encrypt channel data using new password
    
    
def acc_reset() -> None:
    """
    Account reset utility.
    """
    
    print("Are you sure you would like to reset your account?")
    print("(y/n)\n")

    res = input("> ")
    display.clear()

    if res.lower() == "y":
        for file in os.listdir(DATA_DIR):
            os.remove(os.path.join(DATA_DIR, file))
            # remove all user data

        print("Account reset")
        input()
        return

    elif res.lower() != "n":
        print("Error: Invalid input")

    print("Reset aborted")
    input()


def main() -> None:
    """
    Program entry point.
    """
    
    display.clear()
    # clear initial display
    
    while True:
        print("CipherChat configuration menu options:\n")
        print("1 - Credits and information")
        print("2 - Profile selection")
        print("3 - Password reset")
        print("4 - Account reset")
        print("x - Exit\n")
        # program options
        
        option = input("> ")
        display.clear()
        
        match option.lower():
            case "1":
                app_credits()
                # show credits and infromation
            
            case "2":
                profile_select()
                # select profile
            
            case "3":
                pwd_reset()
                # reset password
            
            case "4":
                acc_reset()
                # reset account

            case "x":
                return
                # exit application
            
            case _:
                print("Error: Invalid input")
                input()
                # bad input

        display.clear()


if __name__ == "__main__":
    main()