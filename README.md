[![Build Status](https://travis-ci.org/soulaklabs/tofbot.svg)](https://travis-ci.org/soulaklabs/tofbot)

This is tofbot
==============

Configure and run
-----------------

The bot reads its configuration from the environment. Relevant variables:

    Variable        Default if unspecified  Comment
    TOFBOT_SERVER   irc.freenode.net        -
    TOFBOT_PORT     6667                    -
    TOFBOT_CHAN     #soulakdev              Accepts a comma separated list
    TOFBOT_NICK     tofbot                  -
    TOFBOT_PASSWD   -                       -
    TOFBOT_NAME     tofbot                  -
    TOFBOT_DEBUG    -                       -
    TOFBOT_TIMEOUT  240                     Exit if server does not ping

Launch with Python 3:

    pip install -r requirements.txt
    python bot.py

Check code-style:

    pycodestyle --exclude=tofdata .

Test with Python 3:

    python -m pytest

Test coverage:

    coverage python3 -m pytest
    coverage report
