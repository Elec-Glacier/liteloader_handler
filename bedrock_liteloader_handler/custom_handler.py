import re

from typing_extensions import override
from .bedrock_handler import BedrockServerHandler



class BDSCustomHandler(BedrockServerHandler):
    """
    Custom regex handler for BDS
    """

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