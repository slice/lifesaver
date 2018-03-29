discord.py-lifesaver
====================

.. |py3| image:: https://img.shields.io/badge/python-3.6-blue.svg

.. |license| image:: https://img.shields.io/badge/License-MIT-blue.svg
  :target: https://github.com/slice/lifesaver/blob/master/LICENSE

|py3| |license|

Lifesaver is an extremely opinionated bot foundation built on top of
`discord.py@rewrite <https://github.com/Rapptz/discord.py/tree/rewrite/>`__.

Please be aware that this library contains lots of opinionated features
and hand-holding, and this isn't really meant to be used by anyone — this
repository is open-source just for the sake of being open-source, and for
curious eyes that may be watching.

Features
--------

* Cog baseclass

  * ``Cog.every``: A decorator that makes the cog execute some function
    every *n* seconds with automatic setup and cancellation, along with
    some customization features.

* Custom command class

  * ``command(typing=True)``: Automatically send typing events while this command runs

  * Command group support

* Included extensions (can be disabled!)

  * Administration extension

    * Bot shutdown command

  * Jishaku integration

    * Reload/unload

    * Shell

  * Ping command

  * Errors extension

    * View errors that happen in your bot with a simple "insect" system

    * Basic error handlers for common errors

* Handy utilities

* Built-in storage facilities
