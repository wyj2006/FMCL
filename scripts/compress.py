import os
from glob import glob
from zipfile import ZipFile

os.chdir(os.path.join(os.path.dirname(__file__), ".."))

with ZipFile(os.path.join("src", "package.zip"), mode="w") as zip_file:
    for file_path in set(
        glob("**/*.py", recursive=True)
        + glob("**/function.json", recursive=True)
        + glob("**/defaultsettings.json", recursive=True)
    ) - set(
        glob(".minecraft/**", recursive=True)
        + glob("scripts/**", recursive=True)
        + [os.path.join("resources", "build.py")]
        + glob("target/**", recursive=True)
        + glob("temp/**", recursive=True)
        + glob(".vscode/**", recursive=True)
    ):
        zip_file.write(file_path)
