import os
import subprocess
import sys

os.chdir(os.path.join(os.path.dirname(__file__), ".."))

for root, dirs, files in os.walk("."):
    for file in files:
        name, ext = os.path.splitext(file)
        if ext != ".ui":
            continue
        print(os.path.join(root, file))
        subprocess.run(
            [
                "pyuic6",
                os.path.join(root, file),
                "-o",
                os.path.join(root, f"ui_{name}.py"),
            ],
            stdout=sys.stdout,
            stderr=sys.stdout,
        )
