import re
import json
from typing import Optional, Any
from typing_extensions import override

from mcdreforged.api.utils import Serializable
from .bedrock_handler import BedrockServerHandler, BDSLeviLaminaHandler, BDSScriptHandler, BDSLiteloaderHandler, \
    BDSCustomHandler

DEFAULT_CONFIG = {
    "handler": "BDS",
    "regex_pattern": (
        r">?\s?\[?(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})(?:\.\d+)?\s"
        r"(?P<logging>\w+)"
        r"]?\s?"
        r"(\[[^]]+])\s"  
        r"(?P<content>.*)"
    )
}


class Config(Serializable):
    handler_comment: str = "handler选择值如下: BDS, Liteloader, LeviLamina, Endstore, Script, Custom"
    handler: str = 'BDS'
    regex_pattern: str = (
        r">?\s?\[?(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})(?:\.\d+)?\s"
        r"(?P<logging>\w+)"
        r"]?\s?"
        r"(\[[^]]+])\s"  
        r"(?P<content>.*)"
    )
config: Config

class BDSCustomHandler(BedrockServerHandler):

    custom_regex_pattern: re.Pattern = re.compile('')  # 占位符，稍后动态设置
    @classmethod
    @override
    def get_content_parsing_formatter(cls) -> re.Pattern:
        if not cls.custom_regex_pattern:
            raise ValueError("正则定义有问题")
        return cls.custom_regex_pattern

    @classmethod
    def set_custom_regex(cls, pattern: str):
        try:
            cls.custom_regex_pattern = re.compile(pattern)
        except re.error as e:
            raise ValueError(f"无效的正则表达式: {pattern}") from e

def on_load(server, prev_module):
    global config
    config = server.load_config_simple(
        'config.json',
        default_config=DEFAULT_CONFIG,
        target_class=Config
    )

    if config.handler == 'Liteloader':
        server.logger.info(f"使用Liteloader加载器")
        server.register_server_handler(BDSLiteloaderHandler())
    elif config.handler == 'LeviLamina':
        server.logger.info(f"使用LeviLamina加载器")
        server.register_server_handler(BDSLeviLaminaHandler())
    elif config.handler == 'Endstore':
        server.logger.info(f"Endstore加载器暂时没实现，将使用默认的BDS基类加载器")
        # server.register_server_handler(BDSEndstoreHandler())
        server.register_server_handler(BedrockServerHandler())
    elif config.handler == 'Script':
        server.logger.info(f"使用原版的script api输出加载器")
        server.register_server_handler(BDSScriptHandler())
    elif config.handler == 'BDS':
        server.logger.info(f"将使用默认的BDS基类加载器")
        server.register_server_handler(BedrockServerHandler())
    elif config.handler == 'Other' or config.handler == 'Custom':
        server.logger.info(f"将使用自定义正则加载器")
        try:
            BDSCustomHandler.set_custom_regex(config.regex_pattern)
            server.logger.info(f"自定义正确，将使用自定义正则加载器")
            server.register_server_handler(BDSCustomHandler())
        except ValueError as e:
            server.logger.info(f"自定义错误,错误是:{e} \n 将使用默认的BDS基类加载器")
            server.register_server_handler(BedrockServerHandler())
    else:
        server.logger.info(f"加载器填写错误，将使用默认的BDS基类加载器")
        server.register_server_handler(BedrockServerHandler())



