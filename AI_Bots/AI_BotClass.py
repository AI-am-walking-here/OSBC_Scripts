from abc import ABCMeta

from model.osrs.osrs_bot import OSRSBot, RuneLiteWindow


class AI_BotClass(OSRSBot, metaclass=ABCMeta):
    win: RuneLiteWindow = None

    def __init__(self, bot_title, description) -> None:
        super().__init__("AI_BotClass", bot_title, description)
