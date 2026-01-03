import os

qrc = """<RCC>
  <qresource prefix="/">
"""

for root, dirs, files in os.walk("."):
    for file_name in files:
        name, ext = os.path.splitext(file_name)
        if ext not in (".ico", ".png"):
            continue
        qrc += f"    <file>{os.path.join(root,file_name)}</file>\n"

qrc += """  </qresource>
</RCC>"""

open("resources.qrc", mode="w", encoding="utf-8").write(qrc)
os.system("rcc -g python -o __init__.py resources.qrc")
content = open("__init__.py", encoding="utf-8").read().replace("PySide", "PyQt")
open("__init__.py", mode="w", encoding="utf-8").write(content)
