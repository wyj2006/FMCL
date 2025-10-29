import sys

from setting_editor import SettingEditor

import resources as _
from fmcllib.mirror import MirrorFilter
from fmcllib.setting import SETTING_DEFAULT_PATH
from fmcllib.single_application import SingleApplication
from fmcllib.window import Window

window = None
setting_editor = None

setting_path = SETTING_DEFAULT_PATH
if len(sys.argv) > 1:
    setting_path = sys.argv[1]


def handle():
    global window, setting_editor
    while setting_editor == None:
        pass
    if setting_editor.isVisible():
        return
    if isinstance(setting_editor.window(), Window):
        window = setting_editor.window()
        window.show()
        return
    window = Window(setting_editor)
    window.show()


def main():
    global window, setting_editor
    setting_editor = SettingEditor(setting_path)
    setting_editor.installEventFilter(
        MirrorFilter(
            setting_editor,
            "window",
            lambda w: Window(w).show(),
        )
    )
    window = Window(setting_editor)
    window.show()


app = SingleApplication(sys.argv)
app.firstAppConfirmed.connect(main)
app.otherAppConfirmed.connect(exit)
app.otherAppRun.connect(handle)
app.check(f'settingeditor"{setting_path}"')
sys.exit(app.exec())
