# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# Copyright (c) 2011,2015 Christophe-Marie Duquesne <chmd@chmd.fr>
#                   Martin Kirchgessner <martin.kirch@gmail.com>

"See PluginGetset"

from tofbot.toflib import Plugin, cmd


class PluginGetset(Plugin):
    def __init__(self, bot):
        super(PluginGetset, self).__init__(bot)

    @cmd(1)
    async def cmd_get(self, chan, args, sender_nick):
        "Retrieve a configuration variable's value"
        key = args[0]
        value = self.bot.safe_getattr(key)
        if value is None:
            await self.say("Ne touche pas à mes parties privées !")
        else:
            await self.say("%s = %s" % (key, value))

    @cmd(2)
    async def cmd_set(self, chan, args, sender_nick):
        "Set a configuration variable's value"
        key = args[0]
        value = args[1]
        ok = self.bot.safe_setattr(key, value)
        if not ok:
            await self.say("N'écris pas sur mes parties privées !")
