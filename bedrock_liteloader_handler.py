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
            r'(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2}) '  # 捕获时间部分：小时、分钟、秒
            r'(?P<logging>\w+)'  # 捕获日志级别：INFO, ERROR等
            r' (?:\[[^\]]+\])? '  # 匹配日志来源（如[Server]，可选）
            r'(?P<content>.+)'  # 捕获整个日志消息内容，包括玩家名称和日志内容
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
    def parse_server_stdout(self, text: str) -> Info:
        # print(text + ' I am old')
        # ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        # text = ansi_escape.sub('', text)
        # print(text + ' new')
        result = super().parse_server_stdout(text)
        # 下面print(result)是测试正则结果
        # print(result)

        # content里提取玩家有问题，暂时注释，后续重写
        # for parser in self.__get_player_message_parsers():
        #     if isinstance(parser, parse.Parser):
        #         parsed = parser.parse(result.content)  # TODO: drop parse.Parser support
        #     else:
        #         parsed = parser.fullmatch(result.content)
        #     if parsed is not None and self._verify_player_name(parsed['name']):
        #         result.player, result.content = parsed['name'], parsed['message']
        #         break
        return result

    # ***玩家进入和离开，需要重写
    # __player_joined_regex = re.compile(r'(?P<name>[^\[]+)\[(.*?)] logged in with entity id \d+ at \(.+\)')
    @override
    def parse_player_joined(self, info: Info) -> Optional[str]:
        pass

    # Steve left the game
    # __player_left_regex = re.compile(r'(?P<name>[^ ]+) left the game')
    @override
    def parse_player_left(self, info: Info) -> Optional[str]:
        pass

    # ***确定服务器版本，需要重写
    # __server_version_regex = re.compile(r'Version: (?P<version>.+)')
    @override
    def parse_server_version(self, info: Info) -> Optional[str]:
        pass

    # ***这是确定服务器的ip和端口，需要重写
    # __server_address_regex = re.compile(r'IPv4 supported, port: (?P<ip>\S+):(?P<port>\d+)')
    @override
    def parse_server_address(self, info: Info) -> Optional[Tuple[str, int]]:
        pass

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

