[![Build Status](https://travis-ci.org/soulaklabs/tofbot.svg)](https://travis-ci.org/soulaklabs/tofbot)

This is tofbot
==============

Configure and run
-----------------

The bot reads its configuration from the environment. Relevant variables:

    Variable        Default if unspecified  Comment
    TOFBOT_SERVER   irc.freenode.net        -
    TOFBOT_PORT     6667                    -
    TOFBOT_CHAN     #soulakins              Accepts a comma separated list
    TOFBOT_NICK     tofbot                  -
    TOFBOT_PASSWD   -                       -
    TOFBOT_NAME     tofbot                  -
    TOFBOT_DEBUG    -                       -

Launch with

    python bot.py

Deployment
----------

You need an [openshift](https://www.openshift.com/) account.

    rhc setup
    rhc app create tofbot python-2.7
    git clone https://github.com/tofbot/tofbot.git
    git remote add openshift -f <openshift-git-repo-url>
    git merge openshift/master -s recursive -X ours
    git rm setup.py wsgi.py
    git commit -a -m "removing unused openshift files"
    rhc env set TOFBOT_NICK=bla --app tofbot
    rhc env set TOFBOT_CHAN=\#bla --app tofbot
    rhc env set TOFBOT_CHAN=irc.freenode.net --app tofbot
    rhc env set TOFBOT_PORT=6667 --app tofbot
    git push openshift HEAD

That's all, folks.
