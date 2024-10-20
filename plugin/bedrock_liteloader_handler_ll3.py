import json
import re

from typing_extensions import override

from mcdreforged.handler.impl import AbstractMinecraftHandler
from mcdreforged.info_reactor.server_information import ServerInformation
from mcdreforged.minecraft.rtext.text import RTextBase
from mcdreforged.plugin.meta.version import VersionParsingError
from mcdreforged.utils.types.message import MessageText
from mcdreforged.info_reactor.info import Info

"""
bedrock server handler
"""

PLUGIN_METADATA = {
    'id': 'bedrock_server_ll3',
    'version': '0.2.0',
    'name': 'handling BDS with liteloader modded',
    'description': 'A plugin for bedrock server ll3',
    'author': 'jiangyan03, Elec_glacier',
    'link': 'https://github.com/Elec-Glacier/liteloader_handler'
}


class BedrockServerHandler(AbstractMinecraftHandler):
    """
    A bedrock server handler, handling BDS with liteloader modded
    """

    @override
    def get_name(self) -> str:
        return 'liteloader_handler_ll3'

    # MCDR 获取服务端信息
    @override
    def pre_parse_server_stdout(self, text: str) -> str:
        cleaned_text = ''.join(char for char in text if char not in '\x08\x00-\x1F\x7F')
        print(cleaned_text)
        return cleaned_text

    # 18:25:58.195 INFO [Server] Server started in (3.2s)! For help, type "help" or "?"   ->ll3
    @classmethod
    @override
    def get_content_parsing_formatter(cls) -> re.Pattern:
        return re.compile(
            r'(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2}) '
            r'(?P<logging>\w+)'
            r'( \[[^]]+])'  # thread -> P<thread> #r' (?:\[[^\]]+\])? '
            r' (?P<content>.*)'
        )


    @override
    def get_stop_command(self) -> str:
        return 'stop'

    @override
    def get_send_message_command(self, target: str, message: MessageText, server_information: ServerInformation):
        return 'tellraw "{}" {}'.format(target, self.format_message(message))

    # 服务端信息分离，没有特殊修改勿动
    @override
    def parse_server_stdout(self, text: str):
        result = super().parse_server_stdout(text)
        return result
        pass

    __player_joined_regex = re.compile(r'Player Spawned: (?P<name>[^>]+) xuid: (?P<xuid>\d+)')

    @override
    def parse_player_joined(self, info: Info):
        if not info.is_user:
            if (m := self.__player_joined_regex.fullmatch(info.content)) is not None:
                if self._verify_player_name(m['name']):
                    return m['name']
        return None

    __player_left_regex = re.compile(r'Player disconnected: (?P<name>[^>]+), xuid: (?P<xuid>\d+)')

    @override
    def parse_player_left(self, info: Info):
        if not info.is_user:
            if (m := self.__player_left_regex.fullmatch(info.content)) is not None:
                if self._verify_player_name(m['name']):
                    return m['name']
        return None

    __server_version_regex = re.compile(r'Version:? (?P<version>.+)\((.*)')

    @override
    def parse_server_version(self, info: Info):
        if not info.is_user:
            if (m := self.__server_version_regex.fullmatch(info.content)) is not None:
                return m['version']
        return None

    __server_address_regex = re.compile(r'IPv4 supported, port: (?P<port>\d+)(.*)')

    @override
    def parse_server_address(self, info: Info):
        if not info.is_user:
            if (m := self.__server_address_regex.fullmatch(info.content)) is not None:
                return "127.0.0.1", int(m['port'])
        return None

    # ***检测日志知道服务器的启动完成
    __server_startup_done_regex = re.compile(
        r'(Server started(.*))|(Thanks to RhyMC\(rhymc\.com\) for the support)'  # 1.19.0-1.20.30 ll2/1.17-1.18.30 ll1 or 1.20.30+ ll3
    )

    @override
    def test_server_startup_done(self, info: Info):
        return not info.is_user and self.__server_startup_done_regex.fullmatch(info.content) is not None

    # 测试服务器停止
    @override
    def test_server_stopping(self, info: Info):
        return info.is_from_server and info.content == 'Stopping server...'

    __player_name_regex = re.compile(r'[^>]{3,16}')

    @classmethod
    @override
    def _verify_player_name(cls, name: str):
        return cls.__player_name_regex.fullmatch(name) is not None

    @override
    def format_message(self, message: MessageText) -> str:
        """
        A utility method to convert a message into a valid argument used in message sending command
        """
        message = f"{{\"rawtext\":[{{\"text\":\"{message}\"}}]}}"
        # 我知道这样很蠢，但是这只是权宜之计（，后续修改
        # print(message)
        return message


def on_load(server, prev_module):
    server.register_server_handler(BedrockServerHandler())
