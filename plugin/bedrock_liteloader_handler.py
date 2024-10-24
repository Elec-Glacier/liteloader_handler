import json
import re

from typing_extensions import override

from mcdreforged.handler.impl import AbstractMinecraftHandler
from mcdreforged.info_reactor.server_information import ServerInformation
from mcdreforged.minecraft.rtext.text import RTextBase, RText, RTextList, RTextTranslation
from mcdreforged.plugin.meta.version import VersionParsingError
from mcdreforged.plugin.si.server_interface import ServerInterface
from mcdreforged.utils.types.message import MessageText
from mcdreforged.info_reactor.info import Info
from mcdreforged.plugin.meta.version import Version

"""
bedrock server handler
"""

PLUGIN_METADATA = {
    'id': 'bedrock_server',
    'version': '0.2.4',
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
        """
        不同版本不同日志输出
        eg:
        return re.compile(
            r'>?\s?\[?(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\s'
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
    #         r'>?\s?\[?(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\s'
    #         r'(?P<logging>\w+)'
    #         r']?\s?'
    #         r'(\[[^]]+])\s'  # thread -> P<thread> not use
    #         r'(?P<content>.*)'
    #     )


    # @override
    # def get_stop_command(self) -> str:
    #     return 'stop'

    @override
    def get_send_message_command(self, target: str, message: MessageText, server_information: ServerInformation):
        can_do_execute = False
        if server_information.version is not None:
            try:
                # from mcdreforged.plugin.meta.version import Version
                version = Version(server_information.version.split(' ')[0])
                if version >= Version('1.19.50.0'):
                    can_do_execute = True
            except VersionParsingError:
                pass
        command = 'tellraw {} {}'.format(target, self.format_message(message))
        if can_do_execute:
            command = 'execute at @p run ' + command
        return command

    # -------------------------
    #   Server output parsing
    # -------------------------

    # MCDR 获取服务端信息
    @override
    def pre_parse_server_stdout(self, text: str) -> str:
        # 除去特殊字符串，由于获取1.18.2输出的时候会出现\x08这种操作符，故需要预处理一下服务端的输出
        cleaned_text = ''.join(char for char in text if char not in '\x08\x00-\x1F\x7F')
        return cleaned_text

    # 服务端信息分离，没有特殊修改勿动
    @override
    def parse_server_stdout(self, text: str):
        result = super().parse_server_stdout(text)
        # 由于xboxid存在\s空格字符串，玩家id必须引号处理命令
        if result.player is not None:
            result.player = '"' + result.player + '"'
        return result

    __player_joined_regex = re.compile(r'Player Spawned: (?P<name>[^>]+) xuid: (?P<xuid>\d+)')

    @override
    def parse_player_joined(self, info: Info):
        if not info.is_user:
            if (m := self.__player_joined_regex.fullmatch(info.content)) is not None:
                if self._verify_player_name(m['name']):
                    return '"' + m['name'] + '"'
        return None

    __player_left_regex = re.compile(r'Player disconnected: (?P<name>[^>]+), xuid: (?P<xuid>\d+)')

    @override
    def parse_player_left(self, info: Info):
        if not info.is_user:
            if (m := self.__player_left_regex.fullmatch(info.content)) is not None:
                if self._verify_player_name(m['name']):
                    return '"' + m['name'] + '"'
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
            server_information: ServerInformation = ServerInterface.get_instance().get_server_information()
            if server_information.port is None: # 1.19以下的bds会输出两个ipv4
                if (m := self.__server_address_regex.fullmatch(info.content)) is not None:
                    # 基岩板无法获取ip哦
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
        # 获取服务端的编码暂时搁置，后续写
        # 由于ll2一部分服务端会出现gbk输入，所以为了防止utf8字符变成gbk出现编码错误，需要预处理输入命令
        def replace_utf8_chars(message_):
            replace_dict = {
                '↻': 'R',  # 替换为 [R] 表示刷新
                '↓': 'D',  # 替换为 [D] 表示下载
                '×': 'X',  # 替换为 [X] 表示关闭
            }
            # 替换列表中每个字符串元素
            if isinstance(message_, RTextBase):
                message_str = str(message_)
                for old, new in replace_dict.items():
                    updated_text = message_str.replace(old, new)
                    message_str = updated_text
                return message_str
            return message_

        try:
            message = replace_utf8_chars(message)
        except:
            pass

        # RText需要修改的内容太多了，beje的命令格式不一致，需要大改，只能暂时直接输入命令了
        # if isinstance(message, RTextBase):
        #     print('RTextBase')
        #     print(message.to_json_str())
        # else:
        #     print('ELSE')
        #     print(json.dumps(str(message)))
        message = f"{{\"rawtext\":[{{\"text\":\"{message}\"}}]}}"
        # 我知道这样很蠢，但是这只是权宜之计（，后续修改
        # print(message)
        return message

    # 后续独立优化重写
    # def replace_special_chars(self, message):
    #     """
    #     替换字符串或 RTextBase 对象中的特殊字符。
    #     递归处理 RTextBase 类型对象中的特殊字符，并将其替换为指定字符。
    #     :param message: 字符串或 RTextBase 类型的对象
    #     :return: 替换后的字符串或 RTextBase 对象
    #     """
    #     replace_dict = {
    #         '↻': 'R',  # 替换为 R 表示刷新
    #         '↓': 'D',  # 替换为 D 表示下载
    #         '×': 'X',  # 替换为 X 表示关闭
    #     }
    #
    #     def replace_special_chars_in_text(text: str) -> str:
    #         for old, new in replace_dict.items():
    #             text = text.replace(old, new)
    #         return text
    #
    #     if isinstance(message, str):
    #         # 普通字符串
    #         return replace_special_chars_in_text(message)
    #     elif isinstance(message, RText):
    #         # RText
    #         new_text = replace_special_chars_in_text(str(message))
    #         return RText(new_text, message.color, message.style)
    #     elif isinstance(message, RTextList):
    #         # RTextList ，递归替换
    #         new_rtext_list = RTextList(*[self.replace_special_chars(item) for item in message])
    #         return new_rtext_list
    #     elif isinstance(message, RTextTranslation):
    #         # RTextTranslation ，递归替换
    #         new_args = [self.replace_special_chars(arg) if isinstance(arg, RTextBase) else arg for arg in message.args]
    #         return RTextTranslation(message.translation_key, *new_args)
    #     else:
    #         # other
    #         return message

def on_load(server, prev_module):
    server.register_server_handler(BedrockServerHandler())
