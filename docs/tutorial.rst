Tutorial
========

Welcome to Lifesaver! This narrative document will explain how to get started.

.. currentmodule:: lifesaver

Creating a Bot
--------------

The :class:`Bot` class is the main class that you will creating in your main
script. It will handle configuration loading and the actual startup of your bot.

There are multiple ``Bot`` classes available for use in Lifesaver.
However, they are all subclasses of :class:`BotBase`:

.. class:: lifesaver.bot.BotBase(cfg: lifesaver.bot.BotConfig)

   The base bot class. It contains various components that orchestrate the main
   features of Lifesaver, such as hot reloading and loading of the default
   extensions.

   This class may be instantiated with a :class:`lifesaver.bot.BotConfig`
   instance, but it is generally recommended to use the :meth:`with_config`
   classmethod to load one from a YAML file.

   .. classmethod:: with_config(cls, config = 'config.yml', *, config_cls=BotConfig)

      Creates an instance of this class, configured with a YAML configuration.
      You will want to use this in your startup script.

      :param str config: The file path to the YAML file, typically named
                         "config.yml".
      :param config_cls: The class to use to load the configuration. You can use
                         this kwarg to use your own :class:`BotConfig` subclass.

   .. method:: load_all(self, *, unload_first = False, exclude_default = False)

      Loads all extensions.

      :param bool unload_first: Specifies whether to unload an extension before
                                loading it. This is how the ``reload`` command
                                works.
      :param bool exclude_default: Specifies whether to exclude all default
                                   extensions from being loaded.

   .. method:: run(self)

      Runs this bot from a non-asyncio context, using the token provided in the
      configuration.

There are several different types of bots that you might want to use:

.. class:: lifesaver.bot.Bot

   A regular bot.

.. class:: lifesaver.bot.AutoShardedBot

   An bot that is automatically sharded. You should use this for bots with over
   1,000 guilds.

.. class:: lifesaver.bot.Selfbot

   A selfbot. ``bot=False`` is automatically passed to discord.py, so you don't
   have to think about it.

This is the common pattern that you will want to use when starting a bot:

.. code-block:: python

   Bot.with_config().run()

This code will automatically load a configuration file from ``config.yml`` and
start it up. Here is an example configuration file:

.. code-block:: yaml

   token: '...'
   exts_path: 'exts'

The ``exts_path`` key, defaulting to "./exts", will specify the directory to
automatically load extensions from. If this directory does not exist at startup,
it will refuse to run.

However, with our current code, no extensions will load at all. To provide the
more control over how extensions are loaded, Lifesaver will not load default
extensions by default.

.. code-block:: python
   :emphasize-lines: 2

   bot = Bot.with_config()
   bot.load_all()  # load all extensions
   bot.run()

The call to the :meth:`load_all` method will load all default extensions and
any extensions that are present in the extensions directory, as specified by the
``exts_path`` key in your configuration.

Default Extensions
------------------

The default extensions that are loaded with a bare :meth:`load_all` call are
designed to get the essentials out of the way, so you can focus on the core
features of your bot.

Admin
~~~~~

The Admin cog handles the administration of your bot. All of the commands in
this cog are only available to the owner of the bot, as dictated by the
``commands.is_owner`` check in discord.py.

* ``reload`` (aliases: ``r``)

  Reloads all extensions currently loaded in the bot. If an error is detected in
  an extension, it will not load and an error will be outputted to the console.
  If you fix the issue, running this command again will load it properly.

  **Caveat:** Loading individual extensions is not supported. All extensions
  will be loaded and unloaded every time.

* ``shell`` (aliases: ``sh``)

  Runs a shell command on the system that is running your bot. The process'
  stdout and stderr will be formatted into a code block.

* ``load <extension>``

  Manually loads an extension.

* ``unload <extension>``

  Manually unloads an extension, making it unavailable bot-wide.

* ``die`` (aliases: ``kill``)

  Shuts down the bot completely. There's no going back.

Errors
~~~~~~

This cog handles error messages. It contains a :meth:`on_command_error` event
listener to respond to error messages in a sane manner.

Should an unexpected error be thrown in your bot somewhere, it will respond with
"A fatal error has occurred." along with a UUID. You may pass this UUID into the
``errors view`` command to show the command's backtrace, and when it occurred.
It will also be automatically logged to the console.

Errors are saved into a JSON file in the current working directory using
:class:`AsyncJSONStorage`.

* ``errors view <error_uuid>``

  Views the backtrace of an error by its UUID, and when it occurred.

* ``errors throw``

  Throws an exception or testing the error system.

Customizing error messages that are outputted by the bot is not possible at this
time. If you want to do this, don't load the default extensions and implement it
yourself.

Exec
~~~~

Exec is a very handy cog. Its sole purpose is to execute Python code at runtime.

* ``exec <code>`` (aliases: ``eval``, ``debug``)

  Evaluates code.

* ``cancel``

  Cancels any running code.

Features:

* Implicit return
* Rich execution environment
* Shortcuts and getters
* Cancellable sessions and late indicator
* Execution time measuring
* Smart output formatting and chunking

Specifying code
^^^^^^^^^^^^^^^

Bare code can be passed into the command. You can also surround it with
backticks, both block and inline are recognized. A codeblock with language
specified is also recognized.

Implicit return
^^^^^^^^^^^^^^^

``return`` is automatically added to the end of your code if the syntax ends up
valid. ``return`` is not automatically added if adding it would cause a
:class:`SyntaxError` to occur.

Rich execution environment
^^^^^^^^^^^^^^^^^^^^^^^^^^

Multiple variables are directly accessible from the execution context:

* Self-explanatory: ``bot``, ``ctx``, ``msg``, ``guild``, ``channel``,
  ``cog``

* ``me``: It's the you, represented as a :class:`discord.Member`.

* Modules: ``discord``, ``asyncio``, ``commands``

* Decorators: ``@command``, ``@group``

  For those times you want to add a command or group quickly, for testing.
  You can remove it later with ``bot.remove_command``.

There are also various grabbers:

* ``_g``: Fetches a guild ID.

  .. code-block:: python

     _g(228317351672545290)

* ``_u``: Fetches a user by ID.

* ``_c``: Fetches a channel by ID.

* ``_m``: Fetches a member in this guild. You can specify ID, username, nickname,
  or username#discriminator.

  .. code-block:: python

     _m(97104885337575424)
     _m('slice')
     _m("slice's nickname")
     _m('slice#0001')

The result of the last ``exec`` command is available as ``_``.

Various utilities for operating on data and performing common tasks are also
available:

* ``_send(*args, **kwargs)``

  Sends a message to the current channel. Works just like ``ctx.send``.

* ``_upload(filename: str)``

  Uploads a file to the current channel.

* ``_get``

  Alias to ``discord.utils.get``.

* ``_find``

  Alias to ``discord.utils.find``.

``dir`` is also replaced with an identical version that excludes any magic
methods.

Cancellation and late indicator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Cancel any running code with the ``cancel`` command. Alternatively, you may
use the cancel and kill buttons.

If your code takes at least 5 seconds to run, two reactions will appear on your
message: one of a hourglass, and a knife. The hourglass is simply an indication
that your code is taking a while to run. Reacting with the knife will kill the
running code, as expected.

Execution time
^^^^^^^^^^^^^^

The command automatically measures how long your code takes to run, and will
output it in milliseconds.

Chunked output and formatting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the output of your code is a ``str``, it will not be passed into ``repr``.
Instead, it will be printed and ``(string)`` will be appended to the output
message.

If the length of the output was too long, it will be chunked and DMed to you,
so the channel does not become polluted with large messages. However, it has a
seven page limit.

Health
~~~~~~

The health cog is a simple cog that is used to measure the "health" of your bot.

* ``ping``

  Pings the bot. Heartbeat and REST API latency is reported as a message edit.

Hot Reloading
-------------

Lifesaver has built-in hot reloading to make your life easier when it comes to
developnig extensions. Simply add the following line to your configuration file:

.. code-block:: yaml

   hot_reload: true

Now, any extension that has changed on disk will be reloaded instantly. If an
error is detected, Lifesaver will attempt to reload it on the next file change.
The error is outputted to the console as expected.

This feature works on any operating system that can report file modification
times, because it works by repeatedly polling the filesystem for data.
