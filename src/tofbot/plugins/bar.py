# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# By TaTaaa and piti 2018

from tofbot.toflib import Plugin, cmd, InnocentHand


class PluginBar(Plugin):
    "A bar necessity plugin"

    def __init__(self, bot):
        Plugin.__init__(self, bot)
        # liste des bar autorisés par les Michels
        liste_bar = {
            "L'ouest": ["ouest", "louest", "l'ouest"],
            "Not a Beer": ["notabeer", "ntb"],
            "Paye ta bière": [
                "payetabiere",
                "ptb",
                "payetabière",
                "paietabière",
                "paietabiere",
            ],
            "La Bobine": ["bob", "bobine", "labobine", "labob"],
            "Le Café du Nord": [
                "lecafedunord",
                "lecafédunord",
                "cafedunord",
                "cafédunord",
            ],
            "Le Square": ["lesquare", "square"],
        }
        self.liste_bar = liste_bar

    @cmd(0)
    async def cmd_beer(self, _chan, _args, sender_nick):
        "envoie un bar au hasard"
        if sender_nick in ("Pebz", "P3bz"):
            await self.say("random bar! : Dr D")
        else:
            random_bar = list(self.liste_bar.keys())
            selection = InnocentHand(random_bar)
            await self.say("random bar! : " + selection())
