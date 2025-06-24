import io
import os
import shutil
import sys
import platform
import requests
from zipfile import *

project_path = os.path.dirname(os.path.dirname(__file__))
extract_path = os.path.join(os.path.dirname(__file__), "env")

if sys.platform != "win32":
    raise Exception("Unsupported System")

version_str = (
    f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
)
url = f"https://www.python.org/ftp/python/{version_str}/python-{version_str}-embed-"
match platform.architecture()[0]:
    case "64bit":
        url += "amd64"
    case "32bit":
        url += "win32"
    case _:
        url += "arm64"
url += ".zip"

print(f"Getting: {url}")
r = requests.get(url, stream=True)
contents = b""
for chunk in r.iter_content(102400):
    contents += chunk
    print(f"{round(len(contents)/int(r.headers["Content-Length"])*100,1)}%", end="\r")

zipfile = ZipFile(io.BytesIO(contents))
zipfile.extractall(os.path.join(extract_path, "DLLs"))
print("Extracted DLLs")

lib_zip_name = f"python{sys.version_info.major}{sys.version_info.minor}.zip"
lib_zip = ZipFile(io.BytesIO(zipfile.read(lib_zip_name)))
lib_zip.extractall(os.path.join(extract_path, "Lib"))
print("Extracted Lib")

env_zip = ZipFile(
    os.path.join(project_path, "kernel", "env.zip"),
    mode="w",
    # compression=ZIP_LZMA,
    compresslevel=9,
)
for root, dirs, files in os.walk(extract_path):
    for filename in files:
        if filename == lib_zip_name or ".exe" in filename:
            continue
        if filename.startswith("python") and filename.endswith(".dll"):
            continue
        filepath = os.path.join(root, filename)
        env_zip.write(
            os.path.join(root, filename), os.path.relpath(filepath, extract_path)
        )
        print(f"Added: {filepath}")

shutil.rmtree(extract_path)
