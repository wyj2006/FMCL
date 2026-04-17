from typing import Literal, Optional, TypedDict

import requests
from result import Err, Ok, Result

BASE_URL = "https://api.modrinth.com/v2"


class Error(TypedDict):
    error: str
    description: str


class SearchHit(TypedDict):
    slug: str
    title: str
    description: str
    categories: list[str]
    client_side: Literal["required", "optional", "unsupported", "unknown"]
    server_side: Literal["required", "optional", "unsupported", "unknown"]
    project_type: Literal["mod", "modpack", "resourcepack", "shader"]
    downloads: int
    icon_url: Optional[None]
    color: Optional[None]
    thread_id: str
    monetization_status: Literal["monetized", "demonetized", "force-demonetized"]
    project_id: str
    author: str
    display_categories: list[str]
    versions: list[str]
    follows: int
    date_created: str
    date_modified: str
    latest_version: str
    license: str
    gallery: list[str]
    featured_gallery: Optional[str]


class SearchResponse(TypedDict):
    hits: list[SearchHit]
    offset: int
    limit: int
    total_hits: int


class GetProjectResponse(SearchHit):
    body: str
    status: Literal[
        "approved",
        "archived",
        "rejected",
        "draft",
        "unlisted",
        "processing",
        "withheld",
        "scheduled",
        "private",
        "unknown",
    ]
    requested_status: Literal["approved", "archived", "unlisted", "private", "draft"]
    additional_categories: list[str]
    issues_url: Optional[str]
    source_url: Optional[str]
    wiki_url: Optional[str]
    discord_url: Optional[str]
    donation_urls: list[Donation]
    id: str
    team: str
    body_url: str
    moderator_message: ModeratorMessage
    published: str
    updated: str
    approved: Optional[str]
    queued: Optional[str]
    followers: int
    license: License
    versions: list[str]
    game_versions: list[str]  # 这个对应SearchHit中的versions键
    loaders: list[str]
    gallery: list[Gallery]


class Gallery(TypedDict):
    url: str
    featured: bool
    title: Optional[str]
    description: Optional[str]
    created: str
    ordering: int


class License(TypedDict):
    id: str
    name: str
    url: Optional[str]


class Donation(TypedDict):
    id: str
    platform: str
    url: str


class ModeratorMessage(TypedDict):
    message: str
    body: Optional[str]


class MemberResponse(TypedDict):
    team_id: str
    user: User
    role: str
    permissions: int
    accepted: bool
    payouts_split: int
    ordering: int


class User(TypedDict):
    username: str
    name: Optional[str]
    email: Optional[str]
    bio: str
    payout_data: PayoutData
    id: str
    avatar_url: str
    created: str
    role: Literal["admin", "moderator", "developer"]
    badges: int
    auth_providers: Optional[list[str]]
    email_verified: Optional[bool]
    has_password: Optional[bool]
    has_totp: Optional[bool]


class PayoutData(TypedDict):
    balance: int
    payout_wallet: Literal["paypal", "venmo"]
    payout_wallet_type: Literal["email", "phone", "user_handle"]
    payout_address: str


class VersionResponse(TypedDict):
    name: str
    version_number: str
    changelog: Optional[str]
    dependencies: list[VersionDependence]
    game_versions: list[str]
    version_type: Literal["release", "beta", "alpha"]
    loaders: list[str]
    featured: bool
    status: Literal["listed", "archived", "unlisted", "scheduled", "draft", "unknown"]
    requested_status: Literal["listed", "archived", "unlisted", "draft"]
    id: str
    project_id: str
    author_id: str
    date_published: str
    downloads: int
    changelog_url: Optional[str]
    files: list[VersionFile]


class VersionDependence(TypedDict):
    version_id: Optional[str]
    project_id: Optional[str]
    file_name: Optional[str]
    dependency_type: Literal["required", "optional", "incompatible", "embedded"]


class VersionFile(TypedDict):
    hashes: FileHashes
    url: str
    filename: str
    primary: bool
    size: int
    file_type: Optional[
        Literal[
            "required-resource-pack",
            "optional-resource-pack",
            "sources-jar",
            "jar",
            "dev-jar",
            "javadoc-jar",
            "unknown",
            "signature",
        ]
    ]


class FileHashes(TypedDict):
    sha512: str
    sha1: str


class CategoryResponse(TypedDict):
    icon: str
    name: str
    project_type: str
    header: str


class LoaderResponse(TypedDict):
    icon: str
    name: str
    supported_project_types: list[str]


class GameVersionResponse(TypedDict):
    version: str
    version_type: Literal["release", "snapshot", "alpha", "beta"]
    date: str
    major: bool


def search_project(
    query: str,
    facets: str = "",
    index: Literal[
        "relevance", "downloads", "follows", "newest", "updated"
    ] = "relevance",
    offset=0,
    limit=10,
) -> Result[SearchResponse, str]:
    url = f"{BASE_URL}/search?query={query}&index={index}&{offset=}&{limit=}"
    if facets:
        url += f"&facets={facets}"
    r = requests.get(url).json()
    if "error" in r:
        r: Error
        return Err(f"{r['error']}:{r['description']}")
    return Ok(r)


def get_project(id_or_slug: str) -> Result[GetProjectResponse, str]:
    url = f"{BASE_URL}/project/{id_or_slug}"
    r = requests.get(url)
    if r.status_code == 404:
        return Err(
            "The requested item(s) were not found or no authorization to access the requested item(s)"
        )
    return Ok(r.json())


def get_project_members(id_or_slug: str) -> Result[list[MemberResponse], str]:
    url = f"{BASE_URL}/project/{id_or_slug}/members"
    r = requests.get(url)
    if r.status_code == 404:
        return Err(
            "The requested item(s) were not found or no authorization to access the requested item(s)"
        )
    return Ok(r.json())


def get_team_members(id: str) -> Result[list[MemberResponse], str]:
    url = f"{BASE_URL}/team/{id}/members"
    r = requests.get(url)
    return Ok(r.json())


def list_project_versions(
    id_or_slug: str,
    loaders: list[str] = None,
    game_versions: list[str] = None,
    featured: bool = None,
    include_changelog: bool = False,
) -> Result[list[VersionResponse], str]:
    url = f"{BASE_URL}/project/{id_or_slug}/version?include_changelog={str(include_changelog).lower()}"
    if loaders != None:
        url += f"&loaders={loaders}"
    if game_versions != None:
        url += f"&game_versions={game_versions}"
    if featured != None:
        url += f"&featured={featured}"
    r = requests.get(url)
    if r.status_code == 404:
        return Err(
            "The requested item(s) were not found or no authorization to access the requested item(s)"
        )
    return Ok(r.json())


def get_version(id: str) -> Result[VersionResponse, str]:
    url = f"{BASE_URL}/version/{id}"
    r = requests.get(url)
    if r.status_code == 404:
        return Err(
            "The requested item(s) were not found or no authorization to access the requested item(s)"
        )
    return Ok(r.json())


def get_categories() -> Result[list[CategoryResponse], str]:
    url = f"{BASE_URL}/tag/category"
    return Ok(requests.get(url).json())


def get_loaders() -> Result[list[LoaderResponse], str]:
    url = f"{BASE_URL}/tag/loader"
    return Ok(requests.get(url).json())


def get_gameversions() -> Result[list[GameVersionResponse], str]:
    url = f"{BASE_URL}/tag/game_version"
    return Ok(requests.get(url).json())


def get_projec_types() -> list[str]:
    return requests.get(f"{BASE_URL}/tag/project_type").json()
