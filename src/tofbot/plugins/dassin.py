# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# Copyright (c) 2011 Etienne Millon <etienne.millon@gmail.com>
#                    Martin Kirchgessner <martin.kirch@gmail.com>
import glob
import os
from tofbot.toflib import Plugin, distance


class PluginDassin(Plugin):
    def __init__(self, bot):
        super(PluginDassin, self).__init__(bot)
        self.songs = []
        here = os.path.dirname(os.path.realpath(__file__))
        for path in glob.glob("%s/dassin_data/*.txt" % here):
            self._load_song(path)

    def _load_song(self, path):
        with open(path) as f:
            song = [line.strip() for line in f]
        self.songs.append(song)

    async def handle_msg(self, msg_text, chan, nick):
        searched = msg_text.lower()
        max_dist = len(searched) / 3
        min_dist = 9999999
        best = ""

        for song in self.songs:
            try:
                for i, line in enumerate(song):
                    if abs(len(line) - len(searched)) >= max_dist:
                        continue
                    dist = distance(line, searched)
                    if dist < min_dist:
                        best = song[i + 1]
                        min_dist = dist
            except IndexError:
                pass

        if len(best) > 3 and min_dist < max_dist:
            await self.say(best)
