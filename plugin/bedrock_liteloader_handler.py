import re

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
    'version': '0.1.6',
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

    # [18:23:50 Info] [Server] IPv4 supported, port: 19132    ->ll1
    # 18:25:14 INFO [Server] IPv4 supported, port: 19132: Used for gameplay and LAN discovery   ->ll2
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
        # je的，暂时不需要
        # can_do_execute = False
        # print(self.format_message(message))  # 服务端输出message，调试作用
        # command = 'say {}'.format(self.format_message(message))
        # command = 'tell {} {}'.format(target, self.format_message(message))
        command = 'tellraw {} {}'.format(target, self.format_message(message)) # json不适配，暂时注释
        # if can_do_execute:
        #     command = 'execute at @p run ' + command
        return command

    # -------------------------
    #   Server output parsing
    # -------------------------

    # 信息添加处理，暂时不处理
    # @override
    # def get_broadcast_message_command(self, message: MessageText, server_information: ServerInformation):
    #     return self.get_send_message_command('@a', message, server_information)

    # ***处理玩家信息的总逻辑不需要重写
    @override
    def parse_server_stdout(self, text: str):
        result = super().parse_server_stdout(text)
        # 检测正则结果
        # print(result)
        return result
        pass

    # ***玩家进入和离开，需要重写
    # __player_joined_regex = re.compile(r'(?P<name>[^\[]+)\[(.*?)] logged in with entity id \d+ at \(.+\)')
    __player_joined_regex = re.compile(r'Player Spawned: (?P<name>[^>]+) xuid: (?P<xuid>\d+)')

    @override
    def parse_player_joined(self, info: Info):
        if not info.is_user:
            if (m := self.__player_joined_regex.fullmatch(info.content)) is not None:
                if self._verify_player_name(m['name']):
                    return m['name']
        return None

    # Steve left the game
    # __player_left_regex = re.compile(r'(?P<name>[^ ]+) left the game')
    __player_left_regex = re.compile(r'Player disconnected: (?P<name>[^>]+), xuid: (?P<xuid>\d+)')

    @override
    def parse_player_left(self, info: Info):
        if not info.is_user:
            if (m := self.__player_left_regex.fullmatch(info.content)) is not None:
                if self._verify_player_name(m['name']):
                    return m['name']
        return None

    # ***确定服务器版本，需要重写
    __server_version_regex = re.compile(r'Version: (?P<version>.+)(.*)')

    # Version 1.18.2.03(ProtocolVersion 475) with LiteLoaderBDS 2.0.9
    # Version: 1.20.15.01(ProtocolVersion 594) with LiteLoaderBDS 2.15.0+50eb265
    # Version: 1.21.3.01(ProtocolVersion 686) with LeviLamina-0.13.5+f4a975491
    # Version: 1.21.31.04
    @override
    def parse_server_version(self, info: Info):
        # 如果测试是否匹配成功，可以试试用这个看看控制台的输出）
        # print(self.__server_version_regex.fullmatch(info.content))
        if not info.is_user:
            if (m := self.__server_version_regex.fullmatch(info.content)) is not None:
                return m['version']
        return None

    # ***这是确定服务器的ip和端口，需要重写
    # __server_address_regex = re.compile(r'IPv4 supported, port: (?P<ip>\S+):(?P<port>\d+)')
    # IPv4 supported, port: 19132
    # IPv4 supported, port: 52012: Used for gameplay
    # IPv4 supported, port: 19132: Used for gameplay and LAN discovery
    __server_address_regex = re.compile(r'IPv4 supported, port: (?P<port>\d+)(.*)')

    @override
    def parse_server_address(self, info: Info):
        if not info.is_user:
            if (m := self.__server_address_regex.fullmatch(info.content)) is not None:
                return None, int(m['port'])
        return None

    # ***检测日志知道服务器的启动完成,需要重写
    # eg: 14:29:50:782 INFO [Server] Server started. ll1
    # eg: Vanilla -> [Server] Server started. 但是ll2吞了这个输出）
    # eg: Server started in (3.3s)! For help, type "help" or "?" ll3
    __server_startup_done_regex = re.compile(
        r'(server start(.*))|'  # 1.17-1.18.30 ll1 or 1.20.30+ ll3
        r'(Thanks to RhyMC\(rhymc\.com\) for the support)'  # 1.19.0-1.20.30 ll2
    )

    @override
    def test_server_startup_done(self, info: Info):
        return not info.is_user and self.__server_startup_done_regex.fullmatch(info.content) is not None

    # 测试服务器停止，需要重写
    @override
    def test_server_stopping(self, info: Info):
        return info.is_from_server and info.content == 'Stopping server...'

    __player_name_regex = re.compile(r'[^>]{3,16}')

    @classmethod
    @override
    def _verify_player_name(cls, name: str):
        return cls.__player_name_regex.fullmatch(name) is not None

    @override
    def format_message(cls, message: MessageText) -> str:
        """
        A utility method to convert a message into a valid argument used in message sending command
        """
        message = f"{{\"rawtext\":[{{\"text\":\"{message}\"}}]}}"
        # 我知道这样很蠢，但是这只是权宜之计（，后续修改
        # print(message)
        return message
        # if isinstance(message, RTextBase):
        #     return message.to_json_str()
        # else:
        #     return json.dumps(str(message))


def on_load(server, prev_module):
    server.register_server_handler(BedrockServerHandler())
