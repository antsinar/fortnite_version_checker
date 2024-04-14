import asyncio
from dataclasses import dataclass
from enum import StrEnum
import json
import html.parser
from pathlib import Path
import sys
from typing import AsyncGenerator, List, Generator

import urllib.request

"""
Fetches Reddit posts from FortNiteBR to determine if you are running the latest game version.
Requires Python 3.11.0 or higher.
TODO:
    - support more games on the epic store
    - add settings file support
    - add different parsers for different games and sources
"""


class GAMES_LIST(StrEnum):
    FORTNITE = "Fortnite"


class TerminalColors(StrEnum):
    UP_TO_DATE = "\033[92m"
    LATEST_VERSION = "\033[4m"
    INSTALLED_VERSION = "\033[4m"
    ERROR = "\033[91m"
    BOLD = "\033[1m"
    ENDTEXT = "\033[0m"


class RedditParserMinimal(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.labels: List[str] = list()

    def handle_starttag(self, tag, attrs):
        if tag != "shreddit-post":
            return
        self.labels.append(self._get_title_from_post_title(attrs))

    def handle_endtag(self, tag):
        if tag != "shreddit-post":
            return
        return

    def handle_data(self, data):
        pass

    def _get_title_from_post_title(self, attrs):
        # attr: tuple(name: str, value: str)
        post_title = [attr[1] for attr in attrs if attr[0] == "post-title"]
        return post_title[0]


# JSON schema for settings.json
@dataclass
class Executable:
    name: str | None
    absolute_path: str | None


@dataclass
class Game:
    name: str
    executable: Executable
    source_of_truth: str
    installed_version: str | None = None
    installed_version_file: Path | None = None

    follows_defaults: bool = False


# Not currently used
@dataclass
class Settings:
    games_list: List[Game]


DEFAULT_GAME_ROOT = "C:\\Program Files\\Epic Games"

# TODO: self referencing dict class for name attribute
FORTNITE_DEFAULTS = {
    "name": "Fortnite",
    "executable": Executable(
        **{
            "name": "\\FortniteClient-Win64-Shipping.exe",
            "absolute_path": DEFAULT_GAME_ROOT
            + "\\Fortnite"
            + "\\FortniteGame\\Binaries\\Win64",
        }
    ),
    "source_of_truth": "https://www.reddit.com/r/FortNiteBR/?f=flair_name%3A%22EPIC%22",
    "installed_version_file": DEFAULT_GAME_ROOT
    + "\\Fortnite"
    + "\\Cloud\\cloudcontent.json",
}


def map_game_to_defaults(game_name: str) -> dict | None:
    if game_name == GAMES_LIST.FORTNITE.value:
        return FORTNITE_DEFAULTS
    return None


# feed games to main loop
async def feed_game() -> AsyncGenerator[Game, None]:
    for game in GAMES_LIST:
        default = map_game_to_defaults(game.value)
        if not default:
            continue
        else:
            yield Game(**default, follows_defaults=True)


# validate said items exist as specified in settings
async def installation_exists(executable: Executable, follows_defaults: bool) -> bool:
    if follows_defaults:
        return Path(executable.absolute_path + executable.name).exists()
    return Path(executable.absolute_path).joinpath(executable.name).exists()


async def get_installed_version(game: Game) -> str | None:
    """Fetch installed version from disk"""
    with open(game.installed_version_file, "r") as version_file:
        version = json.load(version_file)
        if "BuildVersion" not in version.keys():
            return None

        return version["BuildVersion"].split("-")[1]


def stream_parsed_content(in_p: str) -> Generator[str, None, None]:
    pass


async def get_latest_version(labels: List[str]) -> str | None:
    """Fetch the latest version from the source of truth
    Relies on the order of the labels being from newest to oldest, as implemented in the Parser class
    """
    for label in labels:
        for instance in label.split():
            if instance.startswith("v") and instance.endswith("0"):
                return instance.replace("v", "")
    return None


# main loop
async def main() -> None:
    version = (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
    # check python version for compatibility
    if version < (3, 11, 0):
        v_string = ".".join(map(str, version))
        print(
            f"{TerminalColors.ERROR}Script expects Python 3.11 or higher, version found: {"".join(v_string)}{TerminalColors.ENDTEXT}"
        )
        exit()

    async for game in feed_game():
        if not await installation_exists(game.executable, game.follows_defaults):
            print(
                f"{TerminalColors.ERROR}[X] {game.name} not found on disk{TerminalColors.ENDTEXT}"
            )
            continue

        game.installed_version = await get_installed_version(game)
        if not game.installed_version:
            print(
                f"{TerminalColors.ERROR}[X] Version for game {game.name} not found, broken cloudcontent (game installation) file{TerminalColors.ENDTEXT}"
            )
            continue

        reddit_parser = RedditParserMinimal()
        with urllib.request.urlopen(game.source_of_truth) as f:
            # TODO: split html byte stream into chunks for less memory usage: stream_parsed_content(in_p)
            if f.status != 200:
                print(
                    f"{TerminalColors.ERROR}[X] Source of truth for game: {game.name} not available, please try again.{TerminalColors.ENDTEXT}"
                )
                continue
            byte_string = f.read()
            reddit_parser.feed(byte_string.decode("utf-8"))

        latest_version = await get_latest_version(reddit_parser.labels)
        if not latest_version:
            print(
                f"{TerminalColors.ERROR}[X] Latest version for game {game.name} not found, please try again.{TerminalColors.ENDTEXT}"
            )
            continue

        if game.installed_version == latest_version:
            print(
                f"{TerminalColors.UP_TO_DATE}[✓] {game.name} is up to date {TerminalColors.ENDTEXT}"
            )
        else:
            print(
                f"[X] Major update available: \n\t[X] {TerminalColors.BOLD}{TerminalColors.LATEST_VERSION}Latest: v{latest_version}{TerminalColors.ENDTEXT}\n\t[X] {TerminalColors.BOLD}{TerminalColors.INSTALLED_VERSION}Installed: v{game.installed_version}{TerminalColors.ENDTEXT}"
            )


asyncio.run(main())
