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
from email import Charset
from email import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.generator import Generator
from cStringIO import StringIO
from toflib import Plugin, cmd


class PluginBar(Plugin):
    "A bar necessity plugin"

    @cmd(1, 100)
    def cmd_bar(self, _chan, _args, sender_nick):
        "writes something"

        heure = _args[0]
        lieu_s = ' '.join(_args[1:])
        lieu = lieu_s.lower().strip().replace(" ", "").decode('utf-8')

        # liste des bar autorisés par les Michels
        liste_bar = [
            u'ouest',
            u'keepitweird', u'kiw',
            u'notabeer',
            u'paietabiere', u'ptb', u'paietabière',
            u'bahaus',
            u'bobine']
        if re.match(r"(1[6-9]|2[0-4])+([hH]$|([hH]+" +
                    "[0-5][0-9])|[:]+[0-5][0-9]+)",
                    heure):  # test de la compatibilité du format de l'heure
            # REGLE: on va au bar entre 16h et 24h59, après c'est fermé,
            # avant c'est être alcoolique
            if lieu in liste_bar:  # teste si le bar proposé est cool
                from_address = [u"Honorable tofbot",
                                "tofbot@ouahpiti.info"]
                pwd = ""
                recipient = [u"Michels", os.getenv(
                    "TOFBOT_MAIL", "grelakins@googlegroups.com")]
                subject = u"Bar ce soir"
                content = u"""Bonsoir les jeunes,
Aujourd'hui, certains Michels vont au bar %s a %s.
Rejoignez les!

Tofbot, au service de %s
                """ % (lieu_s, heure, sender_nick)

                Charset.add_charset('utf-8', Charset.QP, Charset.QP, 'utf-8')
                msg = MIMEMultipart('alternative')
                msg['Subject'] = "%s" % Header(subject, 'utf-8')
                msg['From'] = "\"%s\" <%s>" % (Header(
                    from_address[0], 'utf-8'), from_address[1])
                msg['To'] = "\"%s\" <%s>" % (Header(recipient[0],
                                                    'utf-8'), recipient[1])

                txtpart = MIMEText(content, 'plain', 'UTF-8')
                msg.attach(txtpart)

                str_out = StringIO()
                g = Generator(str_out, False)
                g.flatten(msg)
                mail_server = "localhost"
                server = smtplib.SMTP(mail_server,  25)
                server.ehlo()
                server.sendmail(from_address[1], recipient[1],
                                str_out.getvalue())
                server.quit()
                # message de confirmation de l'envoi de l'email
                self.say(u"Michels avertis!")
            else:  # avertissement bar non autorisé
                self.say(u"J'envoie pas ce mail, ce bar n'est pas cool!")
        else:  # avertissement mauvaise heure
            if re.match(r"^(0[0-9]|1[0-5])", heure):
                # cas de l'heure trop matinale pour un Michel
                self.say(u"Beaucoup trop tôt, mec!")
            else:  # cas d'un format horaire faux
                self.say(u"Euh... L'heure n'est pas claire.")
