from aiogram import Bot
from aiogram.types import BotCommand
from src.utils.lexicon import LEXICON_COMMANDS


async def set_bot_commands(bot: Bot):
    """Setup bot commands in menu"""
    main_menu_commands = [
        BotCommand(command=command, description=description)
        for command, description in LEXICON_COMMANDS.items()
    ]
    await bot.set_my_commands(main_menu_commands)
