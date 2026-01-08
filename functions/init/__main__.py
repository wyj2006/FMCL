import json

from result import is_ok

from fmcllib.filesystem import fileinfo, listdir, mount, mount_native
from fmcllib.function import Function
from fmcllib.setting import Setting, SettingAttrDict

for name in listdir("/functions").unwrap_or([]):
    if is_ok(
        result := fileinfo(
            f"/functions/{name}/defaultsettings.json",
        )
    ):
        for native_path in result.ok_value["native_paths"]:
            mount_native("/defaultsettings.json", native_path)

setting = Setting()
if is_ok(result := fileinfo("/defaultsettings.json")):
    for native_path in result.ok_value["native_paths"]:
        for key, val in json.load(open(native_path, encoding="utf-8")).items():
            val: SettingAttrDict
            if "global" not in val.get("scope", ["global"]):
                continue
            for name, attr in val.items():
                if name == "default_value":
                    setting.add_or_update(key, attr, True)
                else:
                    setting.add_or_update_attr(key, name, attr)

mount("/start", "/functions")
mount("/desktop", "/.minecraft/versions")

for startup in Setting().get("system.startups").unwrap_or([]):
    Function.quick_run(startup["path"], *startup.get("args", []))
