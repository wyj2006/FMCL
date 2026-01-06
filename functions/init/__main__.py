import logging
import traceback

from result import is_ok

from fmcllib.filesystem import fileinfo, listdir, mount, mount_native
from fmcllib.function import Function
from fmcllib.setting import Setting

for name in listdir("/functions").unwrap_or([]):
    if is_ok(
        result := fileinfo(
            f"/functions/{name}/defaultsettings.json",
        )
    ):
        for native_path in result.ok_value["native_paths"]:
            mount_native("/defaultsettings.json", native_path)

mount("/start", "/functions")
mount("/desktop", "/.minecraft/versions")

for startup in Setting().get("system.startups").unwrap_or([]):
    path = startup["path"]
    try:
        Function(path).run(*startup.get("args", [])).unwrap()
    except:
        logging.error(f"无法运行功能'{path}':\n{traceback.format_exc()}")
