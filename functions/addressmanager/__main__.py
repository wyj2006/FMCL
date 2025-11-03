import sys

from PyQt6.QtWidgets import QApplication

from fmcllib.mirror import WindowSource
from fmcllib.window import Window
from functions.addressmanager.address_manager import AddressManager

app = QApplication(sys.argv)
address_manager = AddressManager()
address_manager.installEventFilter(
    WindowSource(
        address_manager,
        lambda w: Window(w).show(),
    )
)
window = Window(address_manager)
window.show()
sys.exit(app.exec())
