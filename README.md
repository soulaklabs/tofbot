This is tofbot
==============

"oh, don't ask why"

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

Launch:

    pip install .
    python bot.py

Check code-style, test, profit:

    pip install -e .[test]
    ruff format
    ruff check
    pytest

Test coverage:

    coverage python3 -m pytest
    coverage report
