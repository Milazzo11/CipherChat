"""
App configuration file reading and setup.

:author: Max Milazzo
"""


import os
import pickle
import yaml
from app.util.paths import (
    USER_CONFIG_PATH, SERVER_CONFIG_PATH, CHANNELS_PATH, ERROR_LOG_PATH
)
from datetime import datetime, timezone
from discord import SyncWebhook


def user_config_load() -> dict:
    """
    Load user configuration data.

    :return: user configuration data
    """

    with open(USER_CONFIG_PATH, "r") as f:
        user_config = yaml.safe_load(f)
        # load user configuration file

    user_config["auth"] = {
        "authorization": user_config["auth"]
    }

    return user_config


def webhook_init(webhooks: list) -> list:
    """
    Initializes webhooks.

    :param webhooks: list of webhook link strings
    :return: list of initialized webhooks
    """
    
    for x in range(len(webhooks)):
        webhooks[x] = SyncWebhook.from_url(webhooks[x])
        
    return webhooks


def server_config_load() -> dict:
    """
    Load server configuration data.

    :return: server configuration data
    """

    with open(SERVER_CONFIG_PATH, "r") as f:
        server_config = yaml.safe_load(f)
        # load server configuration file
        
    server_config["webhooks"] = webhook_init(server_config["webhooks"])
    # initialize webhooks

    return server_config


def channels_load() -> list:
    """
    Sets up and loads channel data.

    :return: channel data
    """

    if os.path.exists(CHANNELS_PATH):
        with open(CHANNELS_PATH, "rb") as f:
            channels = pickle.load(f)
            # load channels
    
    else:
        channels = []
        
        with open(CHANNELS_PATH, "wb") as f:
            pickle.dump(channels, f)
            # write new empty channels pickle file

    return channels


def error_log_reset() -> None:
    """
    Reset error log file.
    """
    
    session_info = f"session: [{datetime.now(tz=timezone.utc)}]"
    
    with open(ERROR_LOG_PATH, "w") as f:
        f.write(
            "=========\n" +
            "ERROR LOG\n" +
            "=========\n" +
            session_info + "\n" +
            "_" * len(session_info) + "\n\n"    
        )


def load() -> tuple:
    """
    Loads data from configuration files.

    :return: loaded data
    """

    user_config = user_config_load()
    # load user configurations

    server_config = server_config_load()
    # load server configurations
        
    channels = channels_load()
    # load channels
            
    error_log_reset()
    # reset error log file
            
    return user_config, server_config, channels