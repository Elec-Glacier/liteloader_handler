from mcdreforged.api.utils import Serializable

from .bedrock_handler import BedrockServerHandler
from .liteloader_handler import BDSLiteloaderHandler
from .levilamina_handler import  BDSLeviLaminaHandler
from .custom_handler import BDSCustomHandler

DEFAULT_CONFIG = {
    "handler": "Liteloader",
    "regex_pattern": ""
}


class Config(Serializable):
    handler_comment: str = "handler to choose: BDS, Liteloader, LeviLamina, Custom"
    handler: str = 'Liteloader'
    Custom_stdout_example: str = '[2024-12-14 06:31:00:773 INFO] [Scripting] [Chat] <Elec glacier> !!MCDR'
    regex_pattern: str = (
            r'\[(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})'
            r' (?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2}):(.*)'
            r' (?P<logging>\w+)]'
            r'( \[[^]]+])?( \[[^]]+])? '
            r'(?P<content>.*)'
        )

config: Config

def on_load(server, prev_module):
    global config
    config = server.load_config_simple(
        'config.json',
        default_config=DEFAULT_CONFIG,
        target_class=Config
    )

    if config.handler == 'Liteloader':
        server.logger.info(f"Loading Liteloader handler")
        server.register_server_handler(BDSLiteloaderHandler())
    elif config.handler == 'LeviLamina':
        server.logger.info(f"Loading LeviLamina_handler")
        server.register_server_handler(BDSLeviLaminaHandler())
    elif config.handler == 'BDS':
        server.logger.info(f"Loading default BDS_handler")
        server.register_server_handler(BedrockServerHandler())
    elif config.handler == 'Other' or config.handler == 'Custom':
        server.logger.info(f"Loading custom regex")
        try:
            BDSCustomHandler.set_custom_regex(config.regex_pattern)
            server.logger.info(f"regex defined correctly, loading custom regex")
            server.register_server_handler(BDSCustomHandler())
        except ValueError as e:
            server.logger.error(f"Invalid custom regex: {e}")
            server.logger.error(f"Regex error, going to load default BDS_handler")
            server.register_server_handler(BedrockServerHandler())
    else:
        server.logger.error(f"Invalid handler: {config.handler}; Going to load default BDS_handler")
        server.register_server_handler(BedrockServerHandler())



