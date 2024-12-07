from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface
from .bedrock_liteloader_handler import BedrockServerHandler

def on_load(server:PluginServerInterface, prev_module):
    server.register_server_handler(BedrockServerHandler())