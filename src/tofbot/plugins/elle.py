# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# Copyright (c) 2015 Christophe-Marie Duquesne <chmd@chmd.fr>

"See PluginElle"

from tofbot.toflib import Plugin


class PluginElle(Plugin):
    "A plugin that asks the right questions"

    async def handle_msg(self, msg_text, _chan, _nick):
        "Que faire lorsqu'un message contient le mot 'elle'"

        words = msg_text.lower().strip().split(" ")

        if "elle" in words:
            if self.tofade_time():
                await self.say("Le vrai win c'est ♥")
