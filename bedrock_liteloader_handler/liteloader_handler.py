import re

from typing_extensions import override
from .bedrock_handler import BedrockServerHandler
from mcdreforged.info_reactor.info import Info



class BDSLiteloaderHandler(BedrockServerHandler):
    """
    Liteloader handler for BDS with Liteloader modded.
    """

    @override
    def get_name(self) -> str:
        return 'BDS_Liteloader_handler'

    @classmethod
    @override
    def get_content_parsing_formatter(cls) -> re.Pattern:
        return re.compile(
            r'>?\s?\[?(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\s'
            r'(?P<logging>\w+)'
            r']?\s?'
            r'(\[(?P<thread>[^]]+)])\s'  # thread -> P<thread> not use
            r'(?P<content>.*)'
        )


    # ll1没有'Server started.'
    __server_startup_done_regex = re.compile(
        r'(Server started(.*))|(Thanks to RhyMC\(rhymc\.com\) for the support)'
    )

    @override
    def test_server_startup_done(self, info: Info):
        return not info.is_user and self.__server_startup_done_regex.fullmatch(info.content) is not None

    # ll1没有Spawned
    __player_joined_regex = re.compile(r'Player connected: (?P<name>[^>]+), xuid: (?P<xuid>\d+)(.*)')

    @override
    def parse_player_joined(self, info: Info):
        if not info.is_user:
            if (m := self.__player_joined_regex.fullmatch(info.content)) is not None:
                if self._verify_player_name(m['name']):
                    return '"' + m['name'] + '"'
        return None

