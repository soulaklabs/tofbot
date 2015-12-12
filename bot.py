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
Usage: ./bot.py

This bot is entirely configured by environment variables. See README.md
for an exaustive list.
"""

from irc import Bot
import random
import sys
import os
import plugins
import types
import json
import atexit
import traceback
import threading
import time
import signal
from toflib import _simple_dispatch, urls_in, Cron, CronEvent

import plugins.help
import plugins.getset
import plugins.ping
import plugins.context
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
import plugins.risoli

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
        self.lolRateDepth = 8
        self.cron = Cron()
        self.lastTGtofbot = 0
        self.memoryDepth = 20
        self.last_interaction = int(time.time())
        self.plugins = self.load_plugins()

    def idle_time(self):
        return int(time.time() - self.last_interaction)

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
        # Useful: https://www.alien.net.au/irc/irc2numerics.html
        self.last_interaction = time.time()
        self.log("o=%s n=%s a=%s" % (origin.sender, origin.nick, args))

        sender_nick = origin.nick
        command_type = args[1]

        if not self.joined:
            self.try_join(args)
            return

        if command_type == 'JOIN':
            for p in self.plugins.values():
                p.on_join(args[0], sender_nick)

        elif command_type == 'KICK' and args[3] == self.nick:
            reason = args[0]
            chan = args[2]
            self.write(('JOIN', chan))
            for p in self.plugins.values():
                p.on_kick(chan, reason)

        elif command_type == 'PRIVMSG':
            self.cron.tick()

            msg_text = args[0]
            chan = args[2]
            urls = urls_in(msg_text)

            # filter empty messages
            if len(msg_text.strip()) == 0:
                return

            # dispatch to plugins
            for p in self.plugins.values():
                p.handle_msg(msg_text, chan, sender_nick)
                for url in urls:
                    p.on_url(url)

            # dispatch commands
            if msg_text.strip().startswith("!"):
                tokens = msg_text.strip().split(" ")
                cmd = tokens[0][1:]
                chan = self.channels[0]
                if cmd in _simple_dispatch:
                    act = self.find_cmd_action("cmd_" + cmd)
                    act(chan, tokens[1:], sender_nick)

        elif command_type == 'PING':
            self.log('PING received in bot.py')

        elif command_type == 'ERROR':
            traceback.print_exc(file=sys.stdout)

        elif command_type == 'PART':
            chan = args[2]
            for p in self.plugins.values():
                p.on_leave(chan, sender_nick)

        elif command_type == 'QUIT':
            for p in self.plugins.values():
                p.on_quit(sender_nick)

        elif command_type == '353':  # Reply to NAMES
            names = set([n.lstrip('@') for n in args[0].split(' ')
                         if n.lstrip('@') != self.nick])
            # act like if everybody just joined
            for n in names:
                for p in self.plugins:
                    if p != "jokes":
                        self.plugins[p].on_join(args[-1], n)

        else:  # Unknown command type
            self.log('Unknown command type : %s' % command_type)

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


def kill_if_disconnected(bot, timeout):
    while True:
        time.sleep(timeout)
        if bot.idle_time() > timeout:
            bot.log("Idle for more than %ds. Exiting..." % timeout)
            os.kill(os.getpid(), signal.SIGINT)
            break


def main():
    host = os.getenv("TOFBOT_SERVER", "irc.freenode.net")
    port = int(os.getenv("TOFBOT_PORT", "6667"))
    chan = os.getenv("TOFBOT_CHAN", "#soulakdev").split(",")
    nick = os.getenv("TOFBOT_NICK", "tofbot")
    password = os.getenv("TOFBOT_PASSWD", None)
    name = os.getenv("TOFBOT_NAME", "tofbot")
    debug = bool(os.getenv("TOFBOT_DEBUG", ""))
    timeout = int(os.getenv("TOFBOT_TIMEOUT", "240"))

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

    t = threading.Thread(target=kill_if_disconnected, args=(b, timeout))
    t.start()
    b.run(host, port)

if __name__ == "__main__":
    main()
