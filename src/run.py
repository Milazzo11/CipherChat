"""
Discord CipherChat.

:author: Max Milazzo
"""


import atexit
from app.lock import lock
from app.util import display


def startup(static: bool = False) -> None:
    """
    Standard program startup initialization.

    :param static: specifies whether channel data is unchanging or has been
        possibly altered via UI interaction during the lifetime of the program
    """

    display.clear()
    # clear initial display
    
    lock.startup(static)
    # correctly handle file unlocking on application start
    
    atexit.register(lambda: lock.encrypt(static))
    # encrypt and write channel data to a file on exit
    
    atexit.register(display.clear)
    # clear display on exit


if __name__ == "__main__":
    startup()
    # initialize program startup

    from app.UI.modules import main, menu
    # import main UI module and menu module

    main.options_button.bind(
        "<Button-1>", lambda event: menu.show_menu(event, main.root)
    )
    # bind main UI and menu modules

    main.root.mainloop()
    # main module UI loop