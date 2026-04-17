import sys

from resource_downloader import ResourceDownloader

import resources as _
from fmcllib.application import Application
from fmcllib.mirror import WindowSource
from fmcllib.window import Window

app = Application(sys.argv)
resource_downloader = ResourceDownloader()
resource_downloader.installEventFilter(
    WindowSource(
        resource_downloader,
        on_detach=lambda w: Window(w).show(),
    )
)
window = Window(resource_downloader)
window.show()
sys.exit(app.exec())
