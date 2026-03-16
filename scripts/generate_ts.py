import json
import os
import subprocess
import sys


def update_json(a) -> list[tuple[str, str]]:
    result = []
    if not isinstance(a, dict):
        return result
    if "translation_context" in a:
        context = a["translation_context"]
        if "value" in a:  # about.json
            result.append((context, a["value"]))
        if "display_name" in a:
            result.append((context, a["display_name"]))
        if "description" in a:  # defaultsettings.json
            result.append((context, a["description"]))
    for _, val in a.items():
        result.extend(update_json(val))
    return result


os.chdir(os.path.join(os.path.dirname(__file__), ".."))

tasks = [
    {
        "target_path": "translations",
        "scan_paths": ["fmcllib", "helps", "defaultsettings.json", "about.json"],
    }
] + [
    {
        "target_path": f"functions/{name}/translations",
        "scan_paths": [f"functions/{name}"],
    }
    for name in os.listdir("functions")
]

for task in tasks:
    sources = []
    paths: list[str] = []

    target_path = task["target_path"]
    os.makedirs(target_path, exist_ok=True)

    for scan_path in task["scan_paths"]:
        if os.path.isdir(scan_path):
            for root, dirs, files in os.walk(scan_path):
                for file in files:
                    paths.append(os.path.join(root, file))
        else:
            paths.append(scan_path)

    for path in paths:
        name, ext = os.path.splitext(path)
        if os.path.basename(path) in (
            "defaultsettings.json",
            "function.json",
            "attribute.json",
            "about.json",
        ):
            temp_path = f"temp/{path.replace("\\","/").replace("/",".")}.py"
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            with open(temp_path, mode="w", encoding="utf-8") as f:
                f.write(f"#{path}\n")
                for context, text in update_json(
                    json.load(open(path, encoding="utf-8"))
                ):
                    f.write(f'translate("{context}","{text}")\n')
                sources.append(f.name)
        if not ext in (".py", ".ui"):
            continue
        sources.append(path)

    for lang in ("en_US",):
        subprocess.run(
            [
                "pylupdate6",
                "--ts",
                os.path.join(target_path, f"{lang}.ts"),
                "--no-obsolete",
                "--verbose",
            ]
            + sources,
            stdout=sys.stdout,
            stderr=sys.stdout,
        )
