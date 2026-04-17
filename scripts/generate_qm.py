import os
import subprocess
import sys

os.chdir(os.path.join(os.path.dirname(__file__), ".."))

for root, dirs, files in os.walk("."):
    for file in files:
        name, ext = os.path.splitext(file)
        if ext != ".ts":
            continue
        subprocess.run(
            [
                "lrelease",
                os.path.join(root, file),
                "-qm",
                os.path.join(root, f"{name}.qm"),
            ],
            stdout=sys.stdout,
            stderr=sys.stdout,
        )
