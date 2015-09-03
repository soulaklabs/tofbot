# -*- coding: utf-8 -*-
# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# Copyright (c) 2011,2015 Christophe-Marie Duquesne <chmd@chmd.fr>
#                   Martin Kirchgessner <martin.kirch@gmail.com>

"See PluginContext"
from toflib import Plugin, cmd


class PluginContext(Plugin):

    def __init__(self, bot):
        super(PluginContext, self).__init__(bot)
        self.msgMemory = []

    def handle_msg(self, msg_text, chan, nick):
        is_cmd = msg_text.strip().startswith('!')
        if chan == self.bot.channels[0] and not is_cmd:
            self.msgMemory.append("<" + nick + "> " + msg_text)
            if len(self.msgMemory) > self.bot.memoryDepth:
                del self.msgMemory[0]

    @cmd(0)
    def cmd_context(self, chan, args, sender_nick):
        "Gives you last messages from the channel"

        intro = "Derniers %s messages envoyés sur %s :" % (
                str(len(self.msgMemory)), self.bot.channels[0])
        self.private(sender_nick, intro)

        for msg in self.msgMemory:
            self.private(sender_nick, msg)
