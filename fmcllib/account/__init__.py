import base64
import json
import logging
import os
from typing import TypedDict

import requests
from PyQt6.QtCore import QCoreApplication, QUrl
from PyQt6.QtGui import QImage, QPixmap
from result import Err, Ok, Result, is_ok

from fmcllib.filesystem import fileinfo, makedirs
from fmcllib.setting import Setting

from .yggdrasil_api import (
    ApiMetaData,
    ProfileInformation,
    TextureProperty,
    YggdrasilApi,
)

DEFAULT_SKIN_PATH = ":/image/skin/wide/steve.png"
tr = QCoreApplication.translate


class SkinDict(TypedDict):
    url: str


class ProfileDict(TypedDict):
    method: str
    player_name: str
    uuid: str
    server_url: str
    access_token: str
    skin: SkinDict


class AuthlibInjectorDict(TypedDict):
    url: str
    metadata: ApiMetaData


def add_account(profile: ProfileDict, setting: Setting = None):
    if setting == None:
        setting = Setting()
    t: list[ProfileDict] = []
    if is_ok(result := setting.get("account.profiles")):
        t = result.ok_value
    t.append(profile)
    setting.set("account.profiles", t)


def delete_account(profile: ProfileDict, setting: Setting = None):
    if setting == None:
        setting = Setting()
    t: list[ProfileDict] = []
    if is_ok(result := setting.get("account.profiles")):
        t = result.ok_value
    try:
        t.remove(profile)
        setting.set("account.profiles", t)
    except ValueError:
        pass


def get_skin_head(skin: QPixmap):
    return skin.copy(8, 8, 8, 8)


def get_authlib_injector_skinurl(server_url: str, id: str):
    api = YggdrasilApi(server_url)
    profile: ProfileInformation = api.query_profile(id)
    for property in profile["properties"]:
        if property["name"] == "textures":
            texture_property: TextureProperty = json.loads(
                base64.b64decode(property["value"])
            )
            for kind, texture in texture_property["textures"].items():
                if kind == "SKIN":
                    return texture["url"]
            break


def default_account_head() -> QPixmap:
    return get_skin_head(QPixmap(DEFAULT_SKIN_PATH))


def get_account_head(profile: ProfileDict) -> QPixmap:
    url = QUrl(profile["skin"]["url"])
    match url.scheme():
        case "qrc":
            return get_skin_head(QPixmap(":" + url.path()))
        case "file":
            return get_skin_head(QPixmap(url.path()))
        case "https" | "http":
            cache_name = url.fileName()
            cache_path = None
            if is_ok(makedirs("/temp/skin")) and is_ok(
                result := fileinfo("/temp/skin")
            ):
                cache_path = os.path.join(
                    result.ok_value["native_paths"][0], cache_name + ".png"
                )
                if os.path.exists(cache_path):
                    return get_skin_head(QPixmap(cache_path))

            pixmap = QPixmap.fromImage(QImage.fromData(requests.get(url.url()).content))
            if cache_path:
                pixmap.save(cache_path)
            return get_skin_head(pixmap)
    return default_account_head()


def add_authlib_injector(server_url: str, setting=None) -> Result[YggdrasilApi, str]:
    if setting == None:
        setting = Setting()
    api = YggdrasilApi(server_url)
    match setting.get("account.authlib_injector_servers"):
        case Ok(t):
            t: list[AuthlibInjectorDict]
            t.append({"url": server_url, "metadata": api.metadata()})
            setting.set("account.authlib_injector_servers", t)
            return Ok(None)
        case Err(e):
            return Err(e)


def signin_authlib_injector(
    authlib_injector: AuthlibInjectorDict,
    username: str,
    password: str,
    setting=None,
) -> Result[None, str]:
    if setting == None:
        setting = Setting()
    api = YggdrasilApi(authlib_injector["url"])
    r = api.signin(username, password)
    logging.debug(f"登录返回: {r}")

    if "errorMessage" in r:
        return Err(r["errorMessage"])
    if "message" in r:
        return Err(r["message"])

    if (
        texture_url := get_authlib_injector_skinurl(
            authlib_injector["url"], r["selectedProfile"]["id"]
        )
    ) == None:
        logging.error(f"无法找到角色的皮肤")
        texture_url = DEFAULT_SKIN_PATH

    add_account(
        {
            "method": "authlib_injector",
            "player_name": r["selectedProfile"]["name"],
            "uuid": r["selectedProfile"]["id"],
            "server_url": authlib_injector["url"],
            "access_token": r["accessToken"],
            "skin": {"url": texture_url},
        },
        setting,
    )
    return Ok(None)


def refresh_account(profile: ProfileDict, setting=None) -> Result[None, str]:
    if setting == None:
        setting = Setting()
    match profile["method"]:
        case "offline":
            pass
        case "authlib_injector":
            api = YggdrasilApi(profile["server_url"])
            r = api.refresh(profile["access_token"])

            if (
                texture_url := get_authlib_injector_skinurl(
                    profile["server_url"], r["selectedProfile"]["id"]
                )
            ) == None:
                logging.error(f"无法找到角色的皮肤")
                texture_url = ""

            t: list[ProfileDict] = []
            if is_ok(result := setting.get("account.profiles")):
                t = result.ok_value
            t[t.index(profile)] |= {  # 只包含了需要刷新键值
                "player_name": r["selectedProfile"]["name"],
                "uuid": r["selectedProfile"]["id"],
                "access_token": r["accessToken"],
                "skin": {"url": texture_url},
            }
            setting.set("account.profiles", t)
        case _:
            raise Err(
                tr("Account", "未知的登录方式:{method}").format(
                    method=profile["method"]
                )
            )
    return Ok(None)
