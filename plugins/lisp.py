# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# Copyright (c) 2016 Guillaume Piolat

"See PluginLisp"
from toflib import Plugin, cmd
import random
from lis import *


class PluginLisp(Plugin):
    "A plugin that provides a minimalistic Lisp interpreter"

    @cmd(1, 100)
    def cmd_lisp(self, _chan, _args, sender_nick):
        "Interpret given LISP expression"
        try:
            line = ' '.join([str(x) for x in _args])
            val = eval(parse(line))
            s = lispstr(val)
            self.say(" => " + s)
#           self.private(sender_nick, " => " + s)
        except Exception, err:
            self.say("Syntax error: " + str(err))
#           self.private(sender_nick, "Syntax error: " + str(err))
