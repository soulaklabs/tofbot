[![Build Status](https://travis-ci.org/tofbot/tofbot.svg)](https://travis-ci.org/tofbot/tofbot)

This is tofbot
==============

configuration files in tofconfigs/

launch for a given configuration like this:

    python bot.py -x tofconfigs/localhost.conf

more help about command line arguments:

    python bot.py -h

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
