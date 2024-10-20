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
    'id': 'bedrock_server',
    'version': '0.2.0',
    'name': 'handling BDS with liteloader modded',
    'description': 'A plugin for bedrock server',
    'author': 'jiangyan03, Elec_glacier',
    'link': 'https://github.com/Elec-Glacier/liteloader_handler'
}


class BedrockServerHandler(AbstractMinecraftHandler):
    """
    A bedrock server handler, handling BDS with liteloader modded
    """

    # 20:35:47 INFO [Server] Version: 1.20.1.02(ProtocolVersion 589) with LiteLoaderBDS 2.14.1+62b3942"
    # 14:19:54 INFO [Server] IPv4 supported, port: 19132: Usedfor gameplay and LAN discovery
    # 14:19:54 INFO [Server] IPv6 supported, port: 19133: Usedor gameplay
    # 18:00:12 INFO [LiteLoader] Thanks to RhyMC(rhymc.com) for the support
    # 18:28:37 INFO [Server] Player connected: Elec glacier, xuid: 2535434141566614
    # 18:28:42 INFO [Server] Player Spawned: Elec glacier xuid: 2535434141566614
    # 18:29:13 INFO [Chat] <Elec glacier> test
    # 18:30:26 INFO [Chat] <Elec glacier> !!MCDR
    # 18:31:04 INFO [Server] Player disconnected: Elec glacier, xuid: 2535434141566614
    # 21:53:36 ERROR [Server] Unknown command: 123. Please check that the command exists and that you have permission to use it.",

    @override
    def get_name(self) -> str:
        return 'liteloader_handler'

    # MCDR 获取服务端信息
    @override
    def pre_parse_server_stdout(self, text: str) -> str:
        cleaned_text = ''.join(char for char in text if char not in '\x08\x00-\x1F\x7F')
        print(cleaned_text)
        return cleaned_text

    # [18:23:50 Info] [Server] IPv4 supported, port: 19132    ->ll1
    # 18:25:14 INFO [Server] IPv4 supported, port: 19132: Used for gameplay and LAN discovery   ->ll2
    # 18:25:58.195 INFO [Server] Server started in (3.2s)! For help, type "help" or "?"   ->ll3



    @classmethod
    @override
    def get_content_parsing_formatter(cls) -> re.Pattern:
        """
        不同版本不同日志输出
        eg:
        return re.compile(
            r'\[?(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\s'
            r'(?P<logging>\w+)'
            r']?\s?'
            r'(\[[^]]+])\s'  # thread -> P<thread> not use
            r'(?P<content>.*)'
        )
        """
        pass


    # @classmethod
    # @override
    # def get_content_parsing_formatter(cls) -> re.Pattern:
    #     return re.compile(
    #         r'(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2}) '
    #         r'(?P<logging>\w+)'
    #         r'( \[[^]]+])'  # thread -> P<thread> #r' (?:\[[^\]]+\])? '
    #         r' (?P<content>.*)'
    #     )


    # @classmethod
    # @override
    # def get_content_parsing_formatter(cls) -> re.Pattern:
    #     return re.compile(
    #         r'\[?(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\s'
    #         r'(?P<logging>\w+)'
    #         r']?\s?'
    #         r'(\[[^]]+])\s'  # thread -> P<thread> not use
    #         r'(?P<content>.*)'
    #     )


    @override
    def get_stop_command(self) -> str:
        return 'stop'

    @override
    def get_send_message_command(self, target: str, message: MessageText, server_information: ServerInformation):
        return 'tellraw “{}” {}'.format(target, self.format_message(message))
        # can_do_execute = False
        # if server_information.version is not None:
        #     try:
        #         from mcdreforged.plugin.meta.version import Version
        #         version = Version(server_information.version.split(' ')[0])
        #         if version >= Version('1.19.50'):
        #             can_do_execute = True
        #     except VersionParsingError:
        #         pass
        # command = 'tellraw {} {}'.format(target, self.format_message(message))
        # if can_do_execute:
        #     command = 'execute at @p run ' + command
        # return command

    # -------------------------
    #   Server output parsing
    # -------------------------

    # 信息添加处理，暂时不处理
    # @override
    # def get_broadcast_message_command(self, message: MessageText, server_information: ServerInformation):
    #     return self.get_send_message_command('@a', message, server_information)

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

    # Version 1.18.2.03(ProtocolVersion 475) with LiteLoaderBDS 2.0.9
    # Version: 1.20.15.01(ProtocolVersion 594) with LiteLoaderBDS 2.15.0+50eb265
    # Version: 1.21.3.01(ProtocolVersion 686) with LeviLamina-0.13.5+f4a975491
    # Version: 1.21.31.04
    __server_version_regex = re.compile(r'Version:? (?P<version>.+)\((.*)')

    @override
    def parse_server_version(self, info: Info):
        if not info.is_user:
            if (m := self.__server_version_regex.fullmatch(info.content)) is not None:
                return m['version']
        return None

    # __server_address_regex = re.compile(r'IPv4 supported, port: (?P<ip>\S+):(?P<port>\d+)')
    # IPv4 supported, port: 19132
    # IPv4 supported, port: 52012: Used for gameplay
    # IPv4 supported, port: 19132: Used for gameplay and LAN discovery
    __server_address_regex = re.compile(r'IPv4 supported, port: (?P<port>\d+)(.*)')

    @override
    def parse_server_address(self, info: Info):
        if not info.is_user:
            if (m := self.__server_address_regex.fullmatch(info.content)) is not None:
                return "127.0.0.1", int(m['port'])
        return None

    # ***检测日志知道服务器的启动完成
    # eg: 14:29:50:782 INFO [Server] Server started. ll1
    # eg: Vanilla -> [Server] Server started. 但是ll2吞了这个输出）
    # eg: Server started in (3.3s)! For help, type "help" or "?" ll3
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
        # print(message)
        # replace_dict = {
        #     '↻': '[R]',  # 替换为 [R] 表示刷新
        #     '↓': '[V]',  # 替换为 [V] 表示下载
        #     '×': '[X]',  # 替换为 [X] 表示关闭
        # }
        message = f"{{\"rawtext\":[{{\"text\":\"{message}\"}}]}}"
        # 我知道这样很蠢，但是这只是权宜之计（，后续修改
        # print(message)
        return message


def on_load(server, prev_module):
    server.register_server_handler(BedrockServerHandler())
