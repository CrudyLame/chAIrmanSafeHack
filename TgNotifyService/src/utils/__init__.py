from src.config import settings
from src.utils.message_builder import MessageBuilder

MESSAGE_BUILDER = MessageBuilder(settings.MESSAGE_TEMPLATES_CONFIG)

__all__ = ["MESSAGE_BUILDER"]
