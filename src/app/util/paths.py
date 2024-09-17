"""
Configuration and data paths.

:author: Max Milazzo
"""


import os


CONFIG_DIR = "config"
# configuration file directory


DATA_DIR = "data"
# data file directory


PROFILES_DIR = "profiles"
# user profile directory


USER_CONFIG_FILENAME = "user.yaml"
# user config filename


SERVER_CONFIG_FILENAME = "server.yaml"
# server config filename


PROFILE_IDENTIFIER_FILENAME = "profile.txt"
# active profile identifier filename


ACTIVE_PROFILE_FLAG_FILENAME = "active.flag"
# active profile flag filename


CHANNELS_FILENAME = "channels.pkl"
# unencrypted pickled channels data filename


ENCRYPTED_CHANNELS_FILENAME = "channels.enc"
# encrypted pickled channels data filename


ERROR_LOG_FILENAME = "error.log"
# error log filename


USER_CONFIG_PATH = os.path.join(CONFIG_DIR, USER_CONFIG_FILENAME)
# user config file path


SERVER_CONFIG_PATH = os.path.join(CONFIG_DIR, SERVER_CONFIG_FILENAME)
# server config file path


PROFILE_IDENTIFIER_PATH = os.path.join(CONFIG_DIR, PROFILE_IDENTIFIER_FILENAME)
# active profile identifier path


CHANNELS_PATH = os.path.join(DATA_DIR, CHANNELS_FILENAME)
# unencrypted pickled channels data file path


ENCRYPTED_CHANNELS_PATH = os.path.join(DATA_DIR, ENCRYPTED_CHANNELS_FILENAME)
# encrypted pickled channels data file path


ERROR_LOG_PATH = os.path.join(DATA_DIR, ERROR_LOG_FILENAME)
# error log file path