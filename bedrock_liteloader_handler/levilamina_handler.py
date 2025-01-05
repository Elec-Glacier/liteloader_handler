import re

from typing_extensions import override
from .bedrock_handler import BedrockServerHandler
from mcdreforged.info_reactor.info import Info

# 05:57:13.995 INFO [PlayerChat] <Elec glacier> !!MCDR  //levilamina

class BDSLeviLaminaHandler(BedrockServerHandler):
    """
    Levilamina handler class
    """
    @override
    def get_name(self) -> str:
        return 'BDS_LeviLamina_handler'

    @classmethod
    @override
    def get_content_parsing_formatter(cls) -> re.Pattern:
        return re.compile(
            r'(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\.(.*)'
            r' (?P<logging>\w+)'
            r' (\[[^]]+])'
            r' (?P<content>.*)'
        )

    __server_startup_done_regex = re.compile(
        r'Server started in \([0-9.]+s\)! For help. type "help" or "\?"'
    )

    @override
    def test_server_startup_done(self, info: Info):
        return not info.is_user and self.__server_startup_done_regex.fullmatch(info.content) is not None