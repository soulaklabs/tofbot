[![Build Status](https://travis-ci.org/tofbot/tofbot.svg)](https://travis-ci.org/tofbot/tofbot)

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

You need an heroku account.

    heroku login
    heroku create
    git push heroku master
    heroku config:set TOFBOT_NICK=bla
    heroku config:set TOFBOT_CHAN=\#bla
    heroku config:set TOFBOT_SERVER=irc.freenode.net
    heroku config:set TOFBOT_PORT=6667
    heroku ps:scale tofbot=1

That's all, folks.
