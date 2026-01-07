import argparse
import sys

from PyQt6.QtCore import QCoreApplication
from setting_editor import SettingEditor

import resources as _
from fmcllib.mirror import WindowSource
from fmcllib.setting import SETTING_DEFAULT_PATH
from fmcllib.single_application import SingleApplication
from fmcllib.window import Window

tr = QCoreApplication.translate

window = None
setting_editor = None

parser = argparse.ArgumentParser()
parser.add_argument(
    "--setting-path",
    help=tr("SettingEditor", "设置文件路径"),
    default=SETTING_DEFAULT_PATH,
)
args = parser.parse_args()
setting_path = args.setting_path


def handle():
    global window, setting_editor
    try:
        if setting_editor.isVisible():
            return
        setting_editor.show()
        if isinstance(setting_editor.window(), Window):
            window = setting_editor.window()
            window.show()
            window.activateWindow()
            return
        window = Window(setting_editor)
        window.show()
    except RuntimeError:
        main()


def main():
    global window, setting_editor

    setting_editor = SettingEditor(setting_path)
    setting_editor.installEventFilter(
        WindowSource(
            setting_editor,
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
