# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# Copyright (c) 2011,2015 Christophe-Marie Duquesne <chmd@chmd.fr>
#                   Martin Kirchgessner <martin.kirch@gmail.com>

"See PluginHelp"

from tofbot.toflib import Plugin, cmd, _simple_dispatch


class PluginHelp(Plugin):
    def __init__(self, bot):
        super(PluginHelp, self).__init__(bot)

    @cmd(0)
    async def cmd_help(self, chan, args, to):
        "Show this help message"
        bot_nick = self.bot.nick
        maxlen = 1 + max(map(len, _simple_dispatch))

        await self.private(
            to,
            "Les commandes doivent être entrées dans le channel ou via message privé",
        )

        for cmd in _simple_dispatch:
            f = self.bot.find_cmd_action("cmd_" + cmd)
            await self.private(to, "%*s - %s" % (maxlen, "!" + cmd, f.__doc__))
        await self.private(
            to,
            "Vous pouvez aussi utiliser !get ou !set sur "
            + ", ".join(self.bot._mutable_attributes.keys()),
        )
