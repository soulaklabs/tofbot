# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# Copyright (c) 2011 Etienne Millon <etienne.millon@gmail.com>
"See PluginEuler"

from tofbot.toflib import Plugin, InnocentHand


class PluginEightBall(Plugin):
    "Magic 8 ball plugin"

    def __init__(self, bot):
        Plugin.__init__(self, bot)
        balldata = [
            "Essaye plus tard",
            "Essaye encore",
            "Pas d'avis",
            "C'est ton destin",
            "Le sort en est jeté",
            "Une chance sur deux",
            "Repose ta question",
            "D'après moi oui",
            "C'est certain",
            "Oui absolument",
            "Tu peux compter dessus",
            "Sans aucun doute",
            "Très probable",
            "Oui",
            "C'est bien parti",
            "C'est non",
            "Peu probable",
            "Faut pas rêver",
            "N'y compte pas",
            "Impossible",
        ]
        self.ball = InnocentHand(balldata)

    async def handle_msg(self, msg_text, _chan, _nick):
        "Reply with a 8 ball answer if input looks like a question"
        msg_text = msg_text.lower().strip()
        if msg_text.startswith("boule magique") and msg_text.endswith("?"):
            await self.say(self.ball())
