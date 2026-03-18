import os
from glob import glob
from zipfile import ZipFile

os.chdir(os.path.join(os.path.dirname(__file__), ".."))

with ZipFile(os.path.join("src", "package.zip"), mode="w") as zip_file:
    for file_path in set(
        glob(os.path.join("**", "*.py"), recursive=True)
        + glob(os.path.join("**", "function.json"), recursive=True)
        + glob(os.path.join("**", "defaultsettings.json"), recursive=True)
        + glob(os.path.join("**", "attribute.json"), recursive=True)
        + glob(os.path.join("**", "*.qml"), recursive=True)
        + glob(os.path.join("**", "*.qm"), recursive=True)
        + glob(os.path.join("**", "about.json"), recursive=True)
    ) - set(
        glob(os.path.join(".minecraft", "**"), recursive=True)
        + list(
            set(glob(os.path.join("scripts", "**"), recursive=True))
            - {
                os.path.join("scripts", "apply_update.py"),
                os.path.join("scripts", "restart.py"),
            }
        )
        + [os.path.join("resources", "build.py")]
        + glob(os.path.join("target", "**"), recursive=True)
        + glob(os.path.join("temp", "**"), recursive=True)
        + glob(os.path.join(".vscode", "**"), recursive=True)
        + glob(os.path.join("**", "functions", "test", "**"), recursive=True)
    ):
        zip_file.write(file_path)
