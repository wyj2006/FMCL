import sys

from account_manager import AccountManager

import resources as _
from fmcllib.mirror import WindowSource
from fmcllib.single_application import SingleApplication
from fmcllib.window import Window

window = None
account_manager = None


def handle():
    global window, account_manager
    while account_manager == None:
        pass
    if account_manager.isVisible():
        return
    if isinstance(account_manager.window(), Window):
        window = account_manager.window()
        window.show()
        window.activateWindow()
        return
    window = Window(account_manager)
    window.show()


def main():
    global window, account_manager
    account_manager = AccountManager()
    account_manager.installEventFilter(
        WindowSource(
            account_manager,
            lambda w: Window(w).show(),
        )
    )
    window = Window(account_manager)
    window.show()


app = SingleApplication(sys.argv)
app.firstAppConfirmed.connect(main)
app.otherAppConfirmed.connect(exit)
app.otherAppRun.connect(handle)
app.check("account_manager")
sys.exit(app.exec())
