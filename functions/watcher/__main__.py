import json
import logging
import os
import time
import traceback

from result import is_ok
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from fmcllib.filesystem import fileinfo, mount_native, unmount_native
from fmcllib.function import Function
from fmcllib.game import Instance
from fmcllib.setting import SETTING_DEFAULT_PATH, Setting


class SettingJsonHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path == SETTING_DEFAULT_PATH:
            update_minecraft_mount()
            update_game()

    def on_modified(self, event):
        if event.src_path == SETTING_DEFAULT_PATH:
            update_minecraft_mount()
            update_game()

    def on_deleted(self, event):
        if event.src_path == SETTING_DEFAULT_PATH:
            update_minecraft_mount()
            update_game()


# 根据 SETTING_DEFAULT_PATH 里的内容更新 /.minecraft 的本地路径
def update_minecraft_mount():
    # 移除旧映射
    for native_path in fileinfo("/.minecraft").unwrap_or({"native_paths": []})[
        "native_paths"
    ]:
        unmount_native("/.minecraft", native_path)

    # 增加新映射
    for game_dir in Setting().get("game.dirs").unwrap_or([]):
        game_dir = os.path.abspath(game_dir)
        mount_native("/.minecraft", game_dir)


# 更新游戏相关的一些文件
def update_game():
    for game_dir in Setting().get("game.dirs").unwrap_or([]):
        try:
            for game_name in os.listdir(os.path.join(game_dir, "versions")):
                instance_path = os.path.join(game_dir, "versions", game_name)
                instance_path = os.path.abspath(instance_path)
                instance = Instance(instance_path)

                # 更新默认设置
                setting = instance.setting
                if is_ok(result := fileinfo("/defaultsettings.json")):
                    for native_path in result.ok_value["native_paths"]:
                        for key, val in json.load(
                            open(native_path, encoding="utf-8")
                        ).items():
                            if "game" not in val.get("scope", ["global"]):
                                continue
                            for name, attr in val.items():
                                if name == "default_value":
                                    setting.add_or_update(key, attr, True)
                                else:
                                    setting.add_or_update_attr(key, name, attr)

                # 同步全局设置
                global_setting = Setting()
                for key in global_setting.get_allkey():
                    scope = global_setting.get_attr(key, "scope").unwrap_or(["global"])
                    if not ("global" in scope and "game" in scope):
                        continue
                    # 如果该设置被更改了, 这句只会更改默认值
                    # 否则会同时更改值和默认值
                    setting.add_or_update(key, global_setting.get(key).unwrap(), True)

                # 更新function.json
                json.dump(
                    {
                        "type": "game",
                        "display_name": game_name,
                        "translation_context": "Game",
                        "icon": {
                            "type": "QIcon",
                            "value": instance.icon_path,
                        },
                        "command": {
                            "template": "function",
                            "program": "/functions/gamemonitor",
                            "args": ["--instance-path", instance_path],
                        },
                    },
                    open(
                        os.path.join(instance_path, "function.json"),
                        mode="w",
                        encoding="utf-8",
                    ),
                    indent=4,
                )
        except:
            logging.error(f"无法更新'{game_dir}': {traceback.format_exc()}")


update_minecraft_mount()
update_game()

observer = Observer()
path = SETTING_DEFAULT_PATH
while not os.path.exists(path):
    path = os.path.dirname(path)
observer.schedule(SettingJsonHandler(), path)
observer.start()

while True:
    time.sleep(1)
    # 只有自己一个功能在运行
    if len(Function.getall_running().unwrap_or([])) <= 1:
        break
