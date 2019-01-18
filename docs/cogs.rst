.. currentmodule: lifesaver

Built-in Cogs
=============

Jishaku
-------

Jishaku is preloaded into every bot that uses Lifesaver. It facilitates bot
administration, debugging, and development.

For more information, visit the `GitHub repo <https://github.com/Gorialis/Jishaku>`_.

Errors
------

Health
------

A ``ping`` command is included in this cog:

.. image:: images/health_cog_ping.png
    :scale: 50%

RTT
~~~

A ``rtt`` command is also implemented, which measures REST API response times
and Gateway echo times for message creation (``MESSAGE_CREATE``) and message
editing (``MESSAGE_UPDATE``).

.. image:: images/health_cog_rtt.png
    :scale: 50%

TX measures the amount of time it takes for the HTTP request to finish. RX
measures how long it takes for the Discord Gateway to echo the action back to
the bot. RTT is the sum of these two values.
