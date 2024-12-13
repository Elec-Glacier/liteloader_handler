import re
import json

from typing_extensions import override

from mcdreforged.handler.impl import AbstractMinecraftHandler
from mcdreforged.info_reactor.server_information import ServerInformation
from mcdreforged.minecraft.rtext.text import RTextBase
from mcdreforged.plugin.meta.version import VersionParsingError
from mcdreforged.plugin.si.server_interface import ServerInterface
from mcdreforged.utils.types.message import MessageText
from mcdreforged.info_reactor.info import Info
from mcdreforged.plugin.meta.version import Version


class BedrockServerHandler(AbstractMinecraftHandler):
    """
    A bedrock server handler, handling BDS with modded
    """

    # [05:45:37 Info][Chat] <Elec glacier> !!MCDR   //liteloader
    # 05:52:33 INFO [Chat] <Elec glacier> !!MCDR    //liteloader v2
    # 05:57:13.995 INFO [PlayerChat] <Elec glacier> !!MCDR  //levilamina
    # [2024-12-14 05:14:30.007 INFO] [Server] <Elec glacier> !!MCDR //Endstone

    @override
    def get_name(self) -> str:
        return 'BDS_handler'

    @classmethod
    @override
    def get_content_parsing_formatter(cls) -> re.Pattern:
        return re.compile(
            r'\[(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})'
            r' (?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2}).(.*)'
            r' (?P<logging>\w+)]'
            r' \[(?P<thread>[^]]+)]'
            r' (?P<content>.*)'
        )

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

    # 除去特殊字符串，由于获取BDS输出的时候会出现\x08等操作符，故需要预处理一下服务端的输出
    @override
    def pre_parse_server_stdout(self, text: str) -> str:
        cleaned_text = ''.join(char for char in text if char not in '\x08\x00\x1F\x7F')
        return cleaned_text

    # 由于xboxid存在\s空格字符串，玩家id必须引号处理命令
    @override
    def parse_server_stdout(self, text: str):
        result = super().parse_server_stdout(text)
        if result.player is not None:
            result.player = '"' + result.player + '"'
        return result

    __player_joined_regex = re.compile(r'Player Spawned: (?P<name>[^>]+) xuid: (?P<xuid>\d+)(.*)')

    @override
    def parse_player_joined(self, info: Info):
        if not info.is_user:
            if (m := self.__player_joined_regex.fullmatch(info.content)) is not None:
                if self._verify_player_name(m['name']):
                    return '"' + m['name'] + '"'
        return None

    __player_left_regex = re.compile(r'Player disconnected: (?P<name>[^>]+), xuid: (?P<xuid>\d+)(.*)')

    @override
    def parse_player_left(self, info: Info):
        if not info.is_user:
            if (m := self.__player_left_regex.fullmatch(info.content)) is not None:
                if self._verify_player_name(m['name']):
                    return '"' + m['name'] + '"'
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
            server_information: ServerInformation = ServerInterface.get_instance().get_server_information()
            if server_information.port is None:  # 1.19以下的bds会输出两个ipv4
                if (m := self.__server_address_regex.fullmatch(info.content)) is not None:
                    # 基岩板无法获取ip
                    return "127.0.0.1", int(m['port'])
        return None

    # ***检测日志知道服务器的启动完成
    __server_startup_done_regex = re.compile(r'Server started.')

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
        try:
            message = self.replace_special_chars(message)
        finally:
            pass
        lines = message.splitlines()
        json_message = []
        for line in lines:
            json_message.append({"text": line})
            json_message.append({"text": "\n"})
        # 移除最后换行
        if json_message and json_message[-1] == {"text": "\n"}:
            json_message.pop()
        output = json.dumps(json_message)
        message = f"{{\"rawtext\":{output}}}"
        return message

    @classmethod
    def replace_special_chars(cls, message):
        replace_dict = {
            '[↻]': '',  #
            '[↓]': '',  #
            '[×]': '',  #
        }
        # 替换列表中每个字符串元素
        if isinstance(message, RTextBase):
            message_str = str(message)
            for old, new in replace_dict.items():
                updated_text = message_str.replace(old, new)
                message_str = updated_text
            return message_str
        return message

class BDSLiteloaderHandler(BedrockServerHandler):
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

    # ll1没有Spawned
    __player_joined_regex = re.compile(r'Player connected: (?P<name>[^>]+) xuid: (?P<xuid>\d+)(.*)')


class BDSLeviLaminaHandler(BedrockServerHandler):
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

class BDSEndstoneHandler(BedrockServerHandler):
    @override
    def get_name(self) -> str:
        return 'BDS_Endstone_handler'
# Endstone的输出跟BDS差不多, 奇怪的是指令输出不了，可以正确解析，但指令无法运行，不知道是不是Endstone也是python构建的原因

class BDSCustomHandler(BedrockServerHandler):
    @override
    def get_name(self) -> str:
        return 'BDS_Custom_handler'

    custom_regex_pattern: re.Pattern = re.compile('')  # 占位符，稍后动态设置
    @classmethod
    @override
    def get_content_parsing_formatter(cls) -> re.Pattern:
        if not cls.custom_regex_pattern:
            raise ValueError("Error in regex defining")
        return cls.custom_regex_pattern

    @classmethod
    def set_custom_regex(cls, pattern: str):
        try:
            cls.custom_regex_pattern = re.compile(pattern)
            return True  # 正则验证通过
        except re.error as e:
            raise ValueError(f"Invalid regex: {pattern}") from e