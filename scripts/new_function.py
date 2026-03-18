import argparse
import os

from case_convert import *

os.chdir(os.path.join(os.path.dirname(__file__), ".."))

parser = argparse.ArgumentParser()
parser.add_argument("name", help="功能名称")
parser.add_argument("--single", help="单例", default=False)

args = parser.parse_args()
name = args.name
is_single = args.single

class_name = pascal_case(name)
module_name = snake_case(name)
function_path = os.path.join("functions", snake_case(name).replace("_", ""))

os.makedirs(function_path, exist_ok=True)

with open(os.path.join(function_path, "__main__.py"), mode="w") as f:
    if not is_single:
        f.write(
            f"""import sys

from {module_name} import {class_name}

import resources as _
from fmcllib.application import Application
from fmcllib.mirror import WindowSource
from fmcllib.window import Window

app=Application(sys.argv)
{module_name} = {class_name}()
{module_name}.installEventFilter(
    WindowSource(
        {module_name},
        on_detach=lambda w: Window(w).show(),
    )
)
window = Window({module_name})
window.show()
sys.exit(app.exec())"""
        )
    else:
        f.write(
            f"""import sys

from {module_name} import {class_name}

import resources as _
from fmcllib.mirror import WindowSource
from fmcllib.single_application import SingleApplication
from fmcllib.window import Window

window = None
{module_name} = None


def handle():
    global window, {module_name}
    try:
        if {module_name}.isVisible():
            return
        {module_name}.show()
        if isinstance({module_name}.window(), Window):
            window = {module_name}.window()
            window.show()
            window.activateWindow()
            return
        window = Window(music{module_name}_player)
        window.show()
    except RuntimeError:
        main()


def main():
    global window, {module_name}
    {module_name} = {class_name}()
    {module_name}.installEventFilter(
        WindowSource(
            {module_name},
            lambda w: Window(w).show(),
        )
    )
    window = Window({module_name})
    window.show()


app = SingleApplication(sys.argv)
app.firstAppConfirmed.connect(main)
app.otherAppConfirmed.connect(exit)
app.otherAppRun.connect(handle)
app.check()
sys.exit(app.exec())
"""
        )

with open(os.path.join(function_path, "function.json"), mode="w") as f:
    f.write(
        f"""{{
    "type": "executable",
    "display_name": "",
    "translation_context": "{class_name}",
    "icon": {{
        "type": "",
        "value": ""
    }},
    "command": {{
        "template": "python"
    }}
}}"""
    )

with open(os.path.join(function_path, f"{module_name}.py"), mode="w") as f:
    f.write(
        f"""from PyQt6.QtWidgets import QWidget
class {class_name}(QWidget):
    def __init__(self):
        super().__init__()"""
    )
