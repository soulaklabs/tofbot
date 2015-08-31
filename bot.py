#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# Copyright (c) 2011,2015 Etienne Millon <etienne.millon@gmail.com>
#                    Martin Kirchgessner <martin.kirch@gmail.com>
#                    Nicolas Dumazet <nicdumz.commits@gmail.com>
#                    Quentin Sabah <quentin.sabah@gmail.com>
#                    Christophe-Marie Duquesne <chm.duquesne@gmail.com>

"""
./bot.py [options] [legacy-arguments]

Legacy-arguments:
    NICK CHANNEL [CHANNEL...]

    Don't prepend a # to chan names
    Tofbot will connect to freenode.net
"""

from datetime import datetime
from irc import Bot
import time
import random
import sys
import os
import plugins
import types
from toflib import _simple_dispatch, urls_in
from toflib import *
import re
from optparse import OptionParser
import json
import atexit
import socket
import traceback

import plugins.euler
import plugins.lolrate
import plugins.donnezmoi
import plugins.jokes
import plugins.twitter
import plugins.dassin
import plugins.eightball
import plugins.sed
import plugins.rick
import plugins.expand
import plugins.like
import plugins.ponce
import plugins.lag

random.seed()


class AutosaveEvent(CronEvent):

    def __init__(self, bot, filename):
        CronEvent.__init__(self, None)
        self.filename = filename
        self.bot = bot

    def fire(self):
        self.bot.save(self.filename)


class Tofbot(Bot):

    # Those attributes are published and can be changed by irc users
    # value is a str to object converter. It could do sanitization:
    # if value is incorrect, raise ValueError
    _mutable_attributes = {
        "TGtime": int,
        "memoryDepth": int
    }

    def __init__(self, nick=None, name=None, channels=None, password=None,
                 debug=True):
        Bot.__init__(self, nick, name, channels, password)
        self.joined = False
        self.autoTofadeThreshold = 98
        self.riddleMaxDist = 2
        self.debug = debug
        self.TGtime = 5
        self.pings = {}
        self.memoryDepth = 20
        self.lolRateDepth = 8
        self.msgMemory = []
        self.cron = Cron()
        self.plugins = self.load_plugins()
        self.startMsgs = []
        self.msgHandled = False

    def load_plugins(self):
        d = os.path.dirname(__file__)
        plugindir = os.path.join(d, 'plugins')
        plugin_instances = {}
        for m in dir(plugins):
            if isinstance(m, types.ModuleType):
                continue
            plugin = getattr(plugins, m)
            for n in dir(plugin):
                c = getattr(plugin, n)
                if type(c) not in [types.ClassType, types.TypeType]:
                    continue
                name = c.__name__
                if name.startswith('Plugin'):
                    instance = c(self)
                    plugin_name = name[6:].lower()
                    plugin_instances[plugin_name] = instance
        return plugin_instances

    # line-feed-safe
    def msg(self, chan, msg):
        self.msgHandled = True
        for m in msg.split("\n"):
            Bot.msg(self, chan, m)

    def log(self, msg):
        if self.debug:
            print(msg)

    def try_join(self, args):
        if args[0] in ("End of /MOTD command.",
                       "This server was created ... I don't know"):
            for chan in self.channels:
                self.write(('JOIN', chan))
            self.joined = True

    def dispatch(self, origin, args):
        self.log("o=%s n=%s a=%s" % (origin.sender, origin.nick, args))

        sender_nick = origin.nick
        commandType = args[1]

        if not self.joined:
            self.try_join(args)
            return

        if commandType == 'JOIN':
            for m in self.startMsgs:
                self.msg(self.channels[0], m)
            self.startMsgs = []
            for p in self.plugins.values():
                p.on_join(args[0], sender_nick)

        elif commandType == 'KICK' and args[3] == self.nick:
            reason = args[0]
            chan = args[2]
            self.write(('JOIN', chan))
            for p in self.plugins.values():
                p.on_kick(chan, reason)

        elif commandType == 'PRIVMSG':
            msg_text = args[0]
            msg = msg_text.strip().split(" ")
            cmd = msg[0]
            chan = args[2]

            self.pings[sender_nick] = datetime.now()

            self.cron.tick()

            if len(cmd) == 0:
                return

            urls = urls_in(msg_text)

            self.msgHandled = False
            # We only allow one plugin to answer, so we trigger them
            # in random order
            for p in self.plugins.values():
                if not self.msgHandled:
                    p.handle_msg(msg_text, chan, sender_nick)
                for url in urls:
                    p.on_url(url)

            if chan == self.channels[0] and cmd[0] != '!':
                self.msgMemory.append("<" + sender_nick + "> " + msg_text)
                if len(self.msgMemory) > self.memoryDepth:
                    del self.msgMemory[0]

            if len(cmd) == 0 or cmd[0] != '!':
                return

            cmd = cmd[1:]

            chan = None
            if len(self.channels) == 0:
                chan = 'config'
            else:
                chan = self.channels[0]

            if cmd in _simple_dispatch:
                act = self.find_cmd_action("cmd_" + cmd)
                act(chan, msg[1:], sender_nick)
            elif cmd == 'context':
                self.send_context(sender_nick)
            elif cmd == 'help':
                self.send_help(sender_nick)

        elif commandType == 'PING':
            self.log('PING received in bot.py')

        elif commandType == 'ERROR':
            traceback.print_exc(file=sys.stdout)

        else:  # Unknown command type
            self.log('Unknown command type : %s' % commandType)

    def find_cmd_action(self, cmd_name):
        targets = self.plugins.values()
        targets.insert(0, self)

        for t in targets:
            if (hasattr(t, cmd_name)):
                action = getattr(t, cmd_name)
                return action

        def nop(self, chan, args):
            pass

        return nop

    def safe_getattr(self, key):
        if key not in self._mutable_attributes:
            return None
        if not hasattr(self, key):
            return "(None)"
        else:
            return str(getattr(self, key))

    def safe_setattr(self, key, value):
        try:
            converter = self._mutable_attributes.get(key)
            if converter is None:
                return False
            value = converter(value)
            setattr(self, key, value)
            return True
        except ValueError:
            pass

    @cmd(1)
    def cmd_ping(self, chan, args):
        "Find when X was last online"
        who = args[0]
        if who in self.pings:
            self.msg(
                chan,
                "Last message from %s was on %s (btw my local time is %s)" %
                (who, self.pings[who].__str__(), datetime.now().__str__())
            )
        else:
            self.msg(chan, "I havn't seen any message from " + who)

    @cmd(1)
    def cmd_get(self, chan, args):
        "Retrieve a configuration variable's value"
        key = args[0]
        value = self.safe_getattr(key)
        if value is None:
            self.msg(chan, "Ne touche pas à mes parties privées !")
        else:
            self.msg(chan, "%s = %s" % (key, value))

    @cmd(2)
    def cmd_set(self, chan, args):
        "Set a configuration variable's value"
        key = args[0]
        value = args[1]
        ok = self.safe_setattr(key, value)
        if not ok:
            self.msg(chan, "N'écris pas sur mes parties privées !")

    def send_context(self, to):
        "Gives you last messages from the channel"

        intro = "Derniers %s messages envoyés sur %s :" % (
                str(len(self.msgMemory)), self.channels[0])
        self.msg(to, intro)

        for msg in self.msgMemory:
            self.msg(to, msg)

    def send_help(self, to):
        "Show this help message"
        maxlen = 1 + max(map(len, _simple_dispatch))

        self.msg(to, "Les commandes doivent être entrées dans le channel "
                 "ou via message privé")

        self.msg(to, '%*s - %s' % (maxlen, "!help", self.send_help.__doc__))
        self.msg(to, '%*s - %s' % (maxlen, "!context",
                 self.send_context.__doc__))

        for cmd in _simple_dispatch:
            f = self.find_cmd_action("cmd_" + cmd)
            self.msg(to, '%*s - %s' % (maxlen, "!" + cmd, f.__doc__))
        self.msg(to, "Vous pouvez aussi utiliser !get ou !set sur " +
                 ", ".join(self._mutable_attributes.keys()))
        self.msg(to, "Si les random-tofades vous ennuient, entrez 'TG " +
                 self.nick + "' (Annulé par 'GG " + self.nick + "')")

    def load(self, filename):
        try:
            with open(filename) as f:
                state = json.load(f)
                if state['version'] != 1:
                    return False
                for name, plugin_state in state['plugins'].items():
                    try:
                        plugin = self.plugins[name]
                        plugin.load(plugin_state)
                    except KeyError:
                        pass
        except IOError as e:
            print "Can't load state. Error: ", e

    def save(self, filename):
        try:
            with open(filename, 'w') as f:
                state = {'version': 1, 'plugins': {}}
                for name, plugin in self.plugins.items():
                    plugin_state = plugin.save()
                    state['plugins'][name] = plugin_state
                json.dump(state, indent=4, fp=f)
        except IOError as e:
            print "Can't save state. Error: ", e


def run():
    host = os.getenv("TOFBOT_SERVER", "irc.freenode.net")
    port = int(os.getenv("TOFBOT_PORT", "6667"))
    chan = os.getenv("TOFBOT_CHAN", "#soulakdev").split(",")
    nick = os.getenv("TOFBOT_NICK", "tofbot")
    password = os.getenv("TOFBOT_PASSWD", None)
    name = os.getenv("TOFBOT_NAME", "tofbot")
    debug = bool(os.getenv("TOFBOT_DEBUG", ""))

    b = Tofbot(nick, name, chan, password, debug)

    # Restore serialized data
    state_file = "state.json"
    b.load(state_file)

    # Perform auto-save periodically
    autosaveEvent = AutosaveEvent(b, state_file)
    b.cron.schedule(autosaveEvent)

    # ... and save at exit
    @atexit.register
    def save_atexit():
        print("Exiting, saving state...")
        b.save(state_file)
        print("Done !")

    b.run(host, port)

if __name__ == "__main__":
    try:
        run()
    except Exception, ex:
        import traceback
        dumpFile = open("_TOFDUMP.txt", "w")
        traceback.print_exc(None, dumpFile)
        dumpFile.close()
        raise ex
