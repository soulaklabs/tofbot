# coding: utf-8
# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# By TaTaaa and piti 2018

import re
import smtplib
import os
import time
from email import Charset
from email import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.generator import Generator
from cStringIO import StringIO
from toflib import Plugin, cmd, InnocentHand


class PluginBar(Plugin):
    "A bar necessity plugin"

    def __init__(self, bot):
        Plugin.__init__(self, bot)
        # liste des bar autorisés par les Michels
        liste_bar = {u"L'ouest": [u'ouest',
                                  u'louest',
                                  u"l'ouest"],
                     u"Keep it Weird": [u'keepitweird',
                                        u'kiw'],
                     u"Not a Beer": [u'notabeer',
                                     u"ntb"],
                     u"Paye ta bière": [
                         u'payetabiere',
                         u'ptb',
                         u'payetabière',
                         u'paietabière',
                         u'paietabiere'],
                     u"Le Bahaus": [u'bahaus',
                                    u"lebauhaus"],
                     u"La Bobine": [
                         u'bob',
                         u'bobine',
                         u'labobine',
                         u'labob'],
                     u"Le Café du Nord": [
                         u'lecafedunord',
                         u'lecafédunord',
                         u'cafedunord',
                         u'cafédunord'],
                     }
        self.liste_bar = liste_bar
        self.liste_grelakins = ("marty_", "p0nce", "piti", "quentin", "TaTaaa")
        self.date_bar = ""

    @cmd(0)
    def cmd_beer(self, _chan, _args, sender_nick):
        "envoie un bar au hasard"
        if sender_nick == "Pebz":
            self.say(u"random bar! : Dr D")
        else:
            random_bar = self.liste_bar.keys()
            selection = InnocentHand(random_bar)
            self.say(u"random bar! : " + selection())

    @cmd(1, 100)
    def cmd_bar(self, _chan, _args, sender_nick):
        "envoie un email aux grelakins"
        # vérification que l'invocateur soit un grelakins
        if sender_nick in self.liste_grelakins:
            # vérification que c'est la première invocation du messager
            if self.date_bar != str(time.strftime('%d/%m/%y',
                                                  time.localtime())):
                heure = _args[0].decode('utf-8')
                lieu = ' '.join(_args[1:]).decode('utf-8')
                lieu = lieu.lower().strip().replace(" ", "")
                if re.match(r"(1[6-9]|2[0-4])+([hH]$|([hH]+" +
                            "[0-5][0-9])|[:]+[0-5][0-9]+)",
                            heure):
                    # test de la compatibilité du format de l'heure
                    # REGLE: on va au bar entre 16h et 24h59,
                    # après c'est fermé, avant c'est être alcoolique
                    for cle, valeur in self.liste_bar.items():
                        if lieu in valeur:  # teste si le bar proposé est cool
                            from_address = [u"Honorable tofbot", os.getenv(
                                "TOFBOT_MAIL", "")]
                            pwd = ""
                            recipient = [u"Michels", os.getenv(
                                "TOFBOT_MAILINGLIST", "")]
                            subject = u"Bar ce soir"
                            content = u"""Bonsoir les jeunes,
Aujourd'hui, certains Michels vont au bar %s à %s.
Rejoignez les!

Tofbot, au service de %s
                            """ % (cle, heure, sender_nick)
                            content = content.encode('utf-8')
                            Charset.add_charset('utf-8',
                                                Charset.QP,
                                                Charset.QP,
                                                'utf-8')
                            msg = MIMEMultipart('alternative')
                            msg['Subject'] = "%s" % Header(subject, 'utf-8')
                            msg['From'] = "\"%s\" <%s>" % (Header(
                                from_address[0], 'utf-8'), from_address[1])
                            msg['To'] = "\"%s\" <%s>" % (
                                Header(recipient[0], 'utf-8'), recipient[1])

                            txtpart = MIMEText(content, 'plain', 'UTF-8')
                            msg.attach(txtpart)

                            str_out = StringIO()
                            g = Generator(str_out, False)
                            g.flatten(msg)
                            mail_server = "localhost"
                            server = smtplib.SMTP(mail_server, 25)
                            server.ehlo()
                            server.sendmail(from_address[1], recipient[1],
                                            str_out.getvalue())
                            server.quit()
                            # message de confirmation de l'envoi de l'email
                            self.say(u"Michels avertis!")
                            self.date_bar = str(time.strftime(
                                '%d/%m/%y',
                                time.localtime()))
                            return
                    # avertissement bar non autorisé
                    self.say(u"J'envoie pas ce mail, ce bar n'est pas cool!")
                else:  # avertissement mauvaise heure
                    if re.match(r"^(0[0-9]|1[0-5])", heure):
                        # cas de l'heure trop matinale pour un Michel
                        self.say(u"Beaucoup trop tôt, mec!")
                    else:  # cas d'un format horaire faux
                        self.say(u"Euh... L'heure n'est pas claire.")
            else:
                self.say(u"Rameutage au bar déjà invoqué aujourd'hui")
        else:
            self.say(u"Seul un Grelakins autorisé peut envoyer un mail !bar")
