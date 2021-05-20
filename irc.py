#!/usr/bin/env python
"""
irc.py - A Utility IRC Bot
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import sys
import re
import time
import traceback
import socket
import asyncore
import asynchat


class Origin(object):
    source = re.compile(r'([^!]*)!?([^@]*)@?(.*)')

    def __init__(self, bot, source, args):
        match = Origin.source.match(source or '')
        self.nick, self.user, self.host = match.groups()

        if len(args) > 1:
            target = args[1]
        else:
            target = None

        mappings = {bot.nick: self.nick, None: None}
        self.sender = mappings.get(target, target)


class Bot(asynchat.async_chat):
    def __init__(self, nick, name, channels, password=None):
        asynchat.async_chat.__init__(self)
        self.set_terminator(b"\n")
        self.buffer = b""

        self.nick = nick
        self.user = nick
        self.name = name
        self.password = password

        self.verbose = True
        self.channels = channels or []
        self.stack = []

        import threading
        self.sending = threading.RLock()

    def initiate_send(self):
        self.sending.acquire()
        asynchat.async_chat.initiate_send(self)
        self.sending.release()

    def __write(self, args, text=None):
        try:
            data = b""
            if text is not None:
                # 510 because CR and LF count too, as nyuszika7h points out
                data = bytes((" ".join(args) + " :" + text)[:510] + "\r\n",
                             encoding='utf8')
            else:
                data = bytes((" ".join(args)[:510] + "\r\n"),
                             encoding='utf8')
            self.push(data)
        except Exception as e:
            print("Error: {0}".format(e), file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)

    def write(self, args, text=None):

        # This is a safe version of __write
        def safe(input):
            if input is None:
                return None
            else:
                return input.replace('\n', '').replace('\r', '')
        try:
            args = [safe(arg) for arg in args]
            text = safe(text)
            self.__write(args, text)
        except Exception as e:
            print("Error in safe({0},{1}): {2}".format(args, text, e),
                  file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)

    def run(self, host, port=6667):
        self.initiate_connect(host, port)

    def initiate_connect(self, host, port):
        if self.verbose:
            print('Connecting to {0}:{1}...'.format(host, port),
                  file=sys.stderr)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        try:
            asyncore.loop()
        except KeyboardInterrupt:
            sys.exit()

    def handle_connect(self):
        if self.verbose:
            print("Connected!", file=sys.stderr)
        if self.password:
            self.write(("PASS", self.password))
        self.write(("NICK", self.nick))
        self.write(("USER", self.user, "+iw", self.nick), self.name)

    def handle_close(self):
        self.close()
        print("Closed!", file=sys.stderr)

    def handle_error(self):
        try:
            raise
        except (KeyboardInterrupt, SystemExit, asyncore.ExitNow):
            raise
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)
        self.close()

    def collect_incoming_data(self, data):
        self.buffer += data

    def found_terminator(self):
        line = self.buffer
        if line.endswith(b"\r"):
            line = line[:-1]
        self.buffer = b""

        line = str(line, 'utf8')

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
        self.dispatch(origin, tuple([text] + args))

        if args[0] == "PING":
            self.write(('PONG', text))

    def dispatch(self, origin, args):
        pass

    def msg(self, recipient, text):
        self.sending.acquire()

        # No messages within the last 3 seconds? Go ahead!
        # Otherwise, wait so it's been at least 0.8 seconds + penalty
        if self.stack:
            elapsed = time.time() - self.stack[-1][0]
            if elapsed < 3:
                penalty = float(max(0, len(text) - 50)) / 70
                wait = 0.8 + penalty
                if elapsed < wait:
                    time.sleep(wait - elapsed)

        # Loop detection
        messages = [m[1] for m in self.stack[-8:]]
        if messages.count(text) >= 5:
            text = '...'
            if messages.count('...') >= 3:
                self.sending.release()
                return

        self.write(("PRIVMSG", recipient), text)
        self.stack.append((time.time(), text))
        self.stack = self.stack[-10:]

        self.sending.release()

    def notice(self, dest, text):
        self.write(("NOTICE", dest), text)


class TestBot(Bot):
    def f_ping(self, origin, match, args):
        delay = m.group(1)
        if delay is not None:
            import time
            time.sleep(int(delay))
            self.msg(origin.sender, 'pong (%s)' % delay)
        else:
            self.msg(origin.sender, 'pong')
    f_ping.rule = r'^\.ping(?:[ \t]+(\d+))?$'


def main():
    print(__doc__)


if __name__ == "__main__":
    main()
