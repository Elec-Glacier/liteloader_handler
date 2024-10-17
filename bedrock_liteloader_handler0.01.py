import re

from typing import Optional, Tuple

from typing_extensions import override

from mcdreforged.handler.impl import AbstractMinecraftHandler
from mcdreforged.info_reactor.server_information import ServerInformation
from mcdreforged.utils.types.message import MessageText
from mcdreforged.info_reactor.info import Info

"""
bedrock server handler
"""

PLUGIN_METADATA = {
    'id': 'bedrock_server',
    'version': '0.0.1',
    'name': 'handling BDS with liteloader modded',
    'description': 'A plugin for bedrock server',
    'author': 'jiangyan03, Elec_glacier',
    'link': 'https://github.com/jiangyan03/MCDReforged-addbedrock',
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

    @classmethod
    @override
    def get_content_parsing_formatter(cls) -> re.Pattern:
        return re.compile(
            r'(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2}) '
            r'(?P<logging>\w+)'
            r'( \[[^]]+])'  # thread -> P<thread>
            r' (?P<content>.*)'
        )

    @override
    def get_stop_command(self) -> str:
        return 'stop'

    @override
    def get_send_message_command(self, target: str, message: MessageText, server_information: ServerInformation) -> Optional[str]:
        can_do_execute = False  # je的，暂时不需要
        print(self.format_message(message))  # 服务端输出message，调试作用
        command = 'say {}'.format(self.format_message(message))
        # command = 'tellraw {} {}'.format(target, self.format_message(message)) json不适配，暂时注释
        if can_do_execute:
            command = 'execute at @p run ' + command
        return command

    # -------------------------
    #   Server output parsing
    # -------------------------

    # 信息添加处理，暂时不处理
    # @override
    # def get_broadcast_message_command(self, message: MessageText, server_information: ServerInformation) -> Optional[
    #     str]:
    #     return self.get_send_message_command('@a', message, server_information)

    # ***处理玩家信息的总逻辑
    @override
    def parse_server_stdout(self, text: str):
        info = super().parse_server_stdout(text)
        if info.player is None:
            m = re.fullmatch(r'<(?P<name>[^>]+)> (?P<message>.*)', info.content)    # 似乎A~ mine hand前面有个[Not secure],这里重写了一遍玩家规则匹配
            if m is not None:   # TODO: verify legal player name
                info.player, info.message = m.group('name'), m.group('message')
        return info

    # ***玩家进入和离开，需要重写
    # __player_joined_regex = re.compile(r'(?P<name>[^\[]+)\[(.*?)] logged in with entity id \d+ at \(.+\)')

    @override
    def parse_player_joined(self, info: Info) -> Optional[str]:
        pass

    __player_joined_regex = re.compile(r'Player connected: (?P<name>[^>]+), xuid: (?P<xuid>\d+)')

    # Player disconnected: Elec glacier, xuid: 2535434141566614
    # Steve left the game
    # __player_left_regex = re.compile(r'(?P<name>[^ ]+) left the game')
    @override
    def parse_player_left(self, info: Info) -> Optional[str]:
        pass

    __player_left_regex = re.compile(r'Player disconnected: (?P<name>[^>]+), xuid: (?P<xuid>\d+)')

    # ***确定服务器版本，需要重写
    # __server_version_regex = re.compile(r'Version: (?P<version>.+)')
    # Version: 1.20.15.01(ProtocolVersion 594) with LiteLoaderBDS 2.15.0+50eb265
    @override
    def parse_server_version(self, info: Info) -> Optional[str]:
        pass

    # ***这是确定服务器的ip和端口，需要重写
    # __server_address_regex = re.compile(r'IPv4 supported, port: (?P<ip>\S+):(?P<port>\d+)')
    # IPv4 supported, port: 19132: Used for gameplay and LAN discovery
    @override
    def parse_server_address(self, info: Info) -> Optional[Tuple[str, int]]:
        pass

    __server_address_regex = re.compile(r'IPv4 supported, port: (?P<port>\d+): Used for gameplay and LAN discovery')
    # ***检测日志知道服务器的启动完成,需要重写
    # eg: 14:29:50:782 INFO [Server] Server started.
    # __server_startup_done_regex = re.compile(
    #     r'Done \([0-9.]+s\)! For help, type "help"'
    #     r'( or "\?")?'  # mc < 1.13
    # )

    @override
    def test_server_startup_done(self, info: Info) -> bool:
        pass

    # 测试服务器停止，需要重写
    @override
    def test_server_stopping(self, info: Info) -> bool:
        return info.is_from_server and info.content == 'Stopping server...'


def on_load(server, prev_module):
    server.register_server_handler(BedrockServerHandler())
