import json
from typing import Any, Literal, NotRequired, TypedDict, Union

import requests

HEADER = {"Content-Type": "application/json; charset=utf-8"}


class ErrorResponse(TypedDict):
    error: str  # 错误的简要描述（机器可读）
    errorMessage: str  # 错误的详细信息（人类可读）
    message: str
    cause: NotRequired[str]  # 该错误的原因（可选）


class UserProperty(TypedDict):
    # preferredLanguage: （可选） 用户的偏好语言，例如 en、zh_CN
    name: Union[str, Literal["preferredLanguage"]]  # 属性的名称
    value: str  # 属性的值


class UserInformation(TypedDict):
    id: str  # 用户的 ID
    properties: list[UserProperty]  # 用户的属性


class TextureDict(TypedDict):
    """textures属性中的textures键的值"""

    url: str  # 材质的 URL
    metadata: dict[str, str]  # 材质的元数据，若没有则不必包含


class TextureProperty(TypedDict):
    """角色属性中的textures属性"""

    timestamp: int  # 该属性值被生成时的时间戳（Java 时间戳格式，即自 1970-01-01 00:00:00 UTC 至今经过的毫秒数）
    profileId: str  # 角色 UUID（无符号）
    profileName: str  # 角色名称
    textures: dict[str, TextureDict]  # 角色的材质


class ProfileProperty(TypedDict):
    name: Union[str, Literal["textures"]]  # 属性的名称
    value: str  # 属性的值
    signature: str  # 属性值的数字签名（仅在特定情况下需要包含）
    # textures: （可选）Base64 编码的 JSON 字符串，包含了角色的材质信息
    # uploadableTextures:（可选）该角色可以上传的材质类型，为 authlib-injector 自行规定的属性


# 这里的profile指的是角色, 跟设置里的profile不一样
class ProfileInformation(TypedDict):
    id: str  # 角色 UUID（无符号）
    name: str  # 角色名称
    # 角色的属性（数组，每一元素为一个属性）（仅在特定情况下需要包含）
    properties: list[ProfileProperty]


class SignInResponse(TypedDict):
    accessToken: str
    clientToken: str
    availableProfiles: list[ProfileInformation]
    selectedProfile: ProfileInformation


class RefreshResponse(TypedDict):
    accessToken: str
    clientToken: str
    selectedProfile: ProfileInformation


class ApiMetaData(TypedDict):
    # 服务端的元数据，内容任意
    meta: dict[
        Union[
            str,
            Literal[
                "serverName",
                "implementationName",
                "implementationVersion",
                "links",
            ],
        ],
        Union[
            Any,
            dict[Literal["homepage", "register"], str],  # 这是links的值
        ],
    ]
    skinDomains: list[str]  # 材质域名白名单
    signaturePublickey: str  # 用于验证数字签名的公钥


class YggdrasilApi:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def metadata(self) -> ApiMetaData:
        url = self.api_url
        r = requests.get(url, headers=HEADER)
        return json.loads(r.content)

    def signin(
        self, username: str, password: str
    ) -> Union[SignInResponse, ErrorResponse]:
        url = f"{self.api_url}/authserver/authenticate"
        r = requests.post(
            url,
            json={
                "username": username,
                "password": password,
                "agent": {"name": "Minecraft", "version": 1},
            },
            headers=HEADER,
        )
        return json.loads(r.content)

    def refresh(self, access_token: str) -> RefreshResponse:
        url = f"{self.api_url}/authserver/refresh"
        r = requests.post(
            url,
            json={"accessToken": access_token},
            headers=HEADER,
        )
        return json.loads(r.content)

    def validate(self, access_token: str) -> bool:
        url = f"{self.api_url}/authserver/validate"
        r = requests.post(
            url,
            json={"accessToken": access_token},
            headers=HEADER,
        )
        return r.status_code == 204

    def invalidate(self, access_token: str):
        url = f"{self.api_url}/authserver/invalidate"
        requests.post(
            url,
            json={"accessToken": access_token},
            headers=HEADER,
        )

    def signout(self, username: str, password: str) -> bool:
        url = f"{self.api_url}/authserver/signout"
        r = requests.post(
            url,
            json={
                "username": username,
                "password": password,
            },
            headers=HEADER,
        )
        return r.status_code == 204

    def query_profile(self, uuid) -> ProfileInformation:
        url = f"{self.api_url}/sessionserver/session/minecraft/profile/{uuid}"
        r = requests.get(url, headers=HEADER)
        return json.loads(r.content)
