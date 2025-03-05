#!/usr/bin/env python
#
# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# Copyright (c) 2011,2016 Etienne Millon <etienne.millon@gmail.com>
#                    Martin Kirchgessner <martin.kirch@gmail.com>
#                    Nicolas Dumazet <nicdumz.commits@gmail.com>
#                    Quentin Sabah <quentin.sabah@gmail.com>
#                    Christophe-Marie Duquesne <chm.duquesne@gmail.com>
#                    Guillaume Piolat <guillaume.piolat@gmail.com>

"""
Usage: ./bot.py

This bot is entirely configured by environment variables. See README.md
for an exaustive list.
"""

import asyncio
import importlib
import inspect
import pkgutil
import random
import sys
import os
import types
import json
import atexit
import traceback
import threading
import time
import signal

from tofbot.irc import Bot
from tofbot.toflib import _simple_dispatch, urls_in, Cron, CronEvent

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
    _mutable_attributes = {"TGtime": int, "memoryDepth": int}

    def __init__(self, nick=None, name=None, channels=None, password=None, debug=True):
        Bot.__init__(self, nick, name, channels, password)
        self.joined = False
        self.autoTofadeThreshold = 98
        self.riddleMaxDist = 2
        self.verbose = debug
        self.TGtime = 5
        self.lolRateDepth = 8
        self.cron = Cron()
        self.lastTGtofbot = 0
        self.memoryDepth = 50
        self.last_interaction = int(time.time())
        self.plugins = self.load_plugins()

    def idle_time(self):
        return int(time.time() - self.last_interaction)

    def load_plugins(self):
        d = os.path.dirname(__file__)
        plugindir = os.path.join(d, "plugins")
        plugin_instances = {}

        # Import all modules from plugins package
        for _, module_name, _ in pkgutil.iter_modules([plugindir]):
            try:
                module = importlib.import_module(f"tofbot.plugins.{module_name}")
            except ImportError:
                continue

            # Find plugin classes in the module - beware that Plugin is always a name in the module
            for attr_name, attr in inspect.getmembers(module, inspect.isclass):
                if attr_name.startswith("Plugin") and len(attr_name) > 6:
                    instance = attr(self)
                    plugin_name = attr_name[6:].lower()
                    plugin_instances[plugin_name] = instance
                    
        return plugin_instances

    # line-feed-safe
    async def msg(self, chan, msg):
        for m in msg.split("\n"):
            await super().msg(self, chan, m)

    def log(self, msg):
        if self.verbose:
            print(msg)

    async def try_join(self, args):
        if args[0] in (
            "End of /MOTD command.",
            "This server was created ... I don't know",
        ):
            for chan in self.channels:
                await self.write(("JOIN", chan))
            self.joined = True

    async def dispatch(self, origin, args):
        # Useful: https://www.alien.net.au/irc/irc2numerics.html
        self.last_interaction = time.time()
        self.log("o=%s n=%s a=%s" % (origin.sender, origin.nick, args))

        sender_nick = origin.nick
        command_type = args[1]

        if not self.joined:
            await self.try_join(args)
            return

        if command_type == "JOIN":
            for p in self.plugins.values():
                await p.on_join(args[0], sender_nick)

        elif command_type == "KICK" and args[3] == self.nick:
            reason = args[0]
            chan = args[2]
            await self.write(("JOIN", chan))
            for p in self.plugins.values():
                await p.on_kick(chan, reason)

        elif command_type == "PRIVMSG":
            self.cron.tick()

            msg_text = args[0]
            chan = args[2]
            urls = urls_in(msg_text)

            # filter empty messages
            if len(msg_text.strip()) == 0:
                return

            # dispatch to plugins
            for p in self.plugins.values():
                await p.handle_msg(msg_text, chan, sender_nick)
                for url in urls:
                    await p.on_url(url)

            # dispatch commands
            if msg_text.strip().startswith("!"):
                tokens = msg_text.strip().split(" ")
                cmd = tokens[0][1:]
                chan = self.channels[0]
                if cmd in _simple_dispatch:
                    act = self.find_cmd_action("cmd_" + cmd)
                    await act(chan, tokens[1:], sender_nick)

        elif command_type == "PING":
            self.log("PING received in bot.py")

        elif command_type == "ERROR":
            traceback.print_exc(file=sys.stdout)

        elif command_type == "PART":
            chan = args[2]
            for p in self.plugins.values():
                await p.on_leave(chan, sender_nick)

        elif command_type == "QUIT":
            for p in self.plugins.values():
                await p.on_quit(sender_nick)

        elif command_type == "353":  # Reply to NAMES
            names = set(
                [
                    n.lstrip("@")
                    for n in args[0].split(" ")
                    if n.lstrip("@") != self.nick
                ]
            )
            # act like if everybody just joined
            for n in names:
                for p in self.plugins:
                    if p != "jokes":
                        await self.plugins[p].on_join(args[-1], n)

        else:  # Unknown command type
            self.log("Unknown command type : %s" % command_type)

    def find_cmd_action(self, cmd_name):
        targets = list(self.plugins.values())
        targets.insert(0, self)

        for t in targets:
            if hasattr(t, cmd_name):
                action = getattr(t, cmd_name)
                return action

        async def nop(self, chan, args):
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
                if state["version"] != 1:
                    return False
                for name, plugin_state in state["plugins"].items():
                    try:
                        plugin = self.plugins[name]
                        plugin.load(plugin_state)
                    except KeyError:
                        pass
        except IOError as e:
            print("Can't load state. Error: {0}".format(e))

    def save(self, filename):
        try:
            with open(filename, "w") as f:
                state = {"version": 1, "plugins": {}}
                for name, plugin in self.plugins.items():
                    plugin_state = plugin.save()
                    state["plugins"][name] = plugin_state
                json.dump(state, indent=4, fp=f)
        except IOError as e:
            print("Can't save state. Error: {0}".format(e))


def kill_if_disconnected(bot, timeout):
    while True:
        time.sleep(timeout)
        if bot.idle_time() > timeout:
            bot.log("Idle for more than %ds. Exiting..." % timeout)
            os.kill(os.getpid(), signal.SIGTERM)
            break


def main():
    host = os.getenv("TOFBOT_SERVER", "irc.libera.chat")
    port = int(os.getenv("TOFBOT_PORT", "6667"))
    chan = os.getenv("TOFBOT_CHAN", "#soulakdev").split(",")
    nick = os.getenv("TOFBOT_NICK", "tofbotdev")
    password = os.getenv("TOFBOT_PASSWD", None)
    name = os.getenv("TOFBOT_NAME", "tofbotdev")
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

    monitor = threading.Thread(target=kill_if_disconnected, args=(b, timeout))
    monitor.daemon = True
    monitor.start()

    asyncio.run(b.run(host, port), debug=debug)


if __name__ == "__main__":
    main()
