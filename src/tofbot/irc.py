#!/usr/bin/env python
"""
irc.py - A Utility IRC Bot

Initial version Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.
http://inamidst.com/phenny/

Reworked by soulaklabs for Python >= 3.12

You'll need to subclass Bot, override `dispath`, and
call `asyncio.run(bot.run(...))`.
"""

import asyncio
from asyncio import StreamReader, StreamWriter
import sys
import re
import time
import traceback


class Origin(object):
    source = re.compile(r"([^!]*)!?([^@]*)@?(.*)")

    def __init__(self, bot, source, args):
        match = Origin.source.match(source or "")
        self.nick, self.user, self.host = match.groups()

        if len(args) > 1:
            target = args[1]
        else:
            target = None

        mappings = {bot.nick: self.nick, None: None}
        self.sender = mappings.get(target, target)


class Bot:
    def __init__(self, nick, name, channels, password=None):
        self.nick = nick
        self.user = nick
        self.name = name
        self.password = password

        self.verbose = True
        self.channels = channels or []
        self.stack = []
        self.writer: StreamWriter = None
        self.reader: StreamReader = None
        self.msg_lock = asyncio.Lock()

    async def run(self, host, port=6667):
        if self.verbose:
            print(f"Connecting to {host}:{port}...", file=sys.stderr)

        self.reader, self.writer = await asyncio.open_connection(host, port)

        if self.verbose:
            print("Connected!", file=sys.stderr)

        if self.password:
            await self.write(("PASS", self.password))
        await self.write(("NICK", self.nick))
        await self.write(("USER", self.user, "+iw", self.nick), self.name)

        await self.message_loop()

    async def write(self, args, text=None):
        # This prevents injection of newlines and carriage returns
        def safe(input):
            if input is None:
                return None
            else:
                return input.replace("\n", "").replace("\r", "")

        try:
            # Sanitize all arguments and text
            args = [safe(arg) for arg in args]
            text = safe(text)

            # 510 because CR and LF count too
            if text is not None:
                data = f"{' '.join(args)} :{text}\r\n"[:510]
            else:
                data = f"{' '.join(args)}\r\n"[:510]

            self.writer.write(data.encode("utf-8"))
            await self.writer.drain()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)

    async def message_loop(self):
        try:
            while True:
                line = await self.reader.readline()
                if not line:
                    break

                line = line.decode("utf-8").strip()

                if line.startswith(":"):
                    source, line = line[1:].split(" ", 1)
                else:
                    source = None

                if " :" in line:
                    argstr, text = line.split(" :", 1)
                else:
                    argstr, text = line, ""

                args = argstr.split()
                origin = Origin(self, source, args)
                await self.dispatch(origin, tuple([text] + args))

                if args[0] == "PING":
                    await self.write(("PONG", text))

        except KeyboardInterrupt:
            sys.exit()
        except Exception as e:
            print(f"Error in message loop: {e}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
        finally:
            if self.writer:
                self.writer.close()
                await self.writer.wait_closed()

    async def dispatch(self, origin, args):
        pass

    async def msg(self, recipient, text):
        async with self.msg_lock:  # Use the instance Lock
            # No messages within the last 3 seconds? Go ahead!
            # Otherwise, wait so it's been at least 0.8 seconds + penalty
            if self.stack:
                elapsed = time.time() - self.stack[-1][0]
                if elapsed < 3:
                    penalty = float(max(0, len(text) - 50)) / 70
                    wait = 0.8 + penalty
                    if elapsed < wait:
                        await asyncio.sleep(wait - elapsed)

            # Loop detection
            messages = [m[1] for m in self.stack[-8:]]
            if messages.count(text) >= 5:
                text = "..."
                if messages.count("...") >= 3:
                    return

            await self.write(("PRIVMSG", recipient), text)
            self.stack.append((time.time(), text))
            self.stack = self.stack[-10:]

    async def notice(self, dest, text):
        await self.write(("NOTICE", dest), text)


def main():
    print(__doc__)


if __name__ == "__main__":
    main()
