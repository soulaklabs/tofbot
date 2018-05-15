# coding: utf-8
# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# By TaTaaa 2018

from toflib import Plugin
import time
from unidecode import unidecode
import re


class PluginAmour(Plugin):
    # determination of the win in the dating game

    def handle_msg(self, msg_text, _chan, _nick):
        # calcule les chances si la synthaxe de la chaine
        # matche grande irma, chaine1<3chaine2?
        chaine = msg_text.lower().strip()
        if re.match(r"(grande irma,)\s*[a-zA-Z_]+.*<3(.)*[a-zA-Z_]+.*(\?)+",
                    chaine):
            # séparation des deux prénoms
            chaine = chaine.replace(" ", "")
            chaine = chaine.replace('grandeirma,', '')
            chaine = chaine[:-1]
            amoureux1, amoureux2 = chaine.split("<3")

            # concaténation des deux chaines
            chaine = amoureux1 + amoureux2

            # suppression des caractènes n'étant pas des lettres
            chaine = re.sub("[^a-zA-Z_]", "", chaine)

            # transposition des lettres en identifiant numérique
            chaine = [ord(lettre) for lettre in chaine.lower()]

            # calcul de la somme theologique (theonum) de tous
            # les identifiants numériques
            theonum = sum(chaine)

            # boucle sur theonum pour que la somme finale soit comprise
            # entre 1 et 9
            while theonum > 9:
                chaine = [int(i) for i in str(theonum)]
                theonum = sum(chaine)
            # calcul du pourcentage de l'amour calibré sur
            # Vanessa et Erick = 100%
            pourcentage = (11 - theonum) * 10
            text = "   " + str(pourcentage) + '% de réussite pour ' + \
                   amoureux1 + ' et ' + amoureux2

            if pourcentage < 40:  # pour les plans cul
                self.say(u"»-(¯`·.·´¯)-> Irma prédit l'Amour <-(¯`·.·´¯)-«")
                self.say(" ")
                time.sleep(0.5)
                self.say(text)
                self.say(" ")
                self.say('8==D    8==D    8==D    8==D    8==D    8==D')

            else:  # pour le vrai win
                self.say(u"»-(¯`·.·´¯)-> Irma prédit L'amour <-(¯`·.·´¯)-«")
                self.say(" ")
                time.sleep(0.5)
                self.say(text)
                self.say(" ")
                self.say('<3 <3 <3 <3 <3 <3 <3 <3 <3 <3 <3 <3 <3 <3 <3')
