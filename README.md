# discord.py-lifesaver

![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)
![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Lifesaver is an opinionated Discord bot framework built on top of
[discord.py][dpy]. It exports an assortment of utilities and helpers that eases
the burden of maintenance when it comes to everyday botmaking, and is especially
handy to those who maintain multiple bots at a time.

> **Warning**: Lifesaver is a glorified deduplication of common code that the
> author found himself needing across bots, and is not inherently useful to
> everyone.

## Features

- Built-in cogs
  - [jishaku][jsk]
  - Command error handler (`Errors`)
  - Ping (`Health`)
- Extension hot reloading via filesystem polling
- Bot (and cog) configuration primitives
- Command line module (`python -m lifesaver.cli`) for starting bots
- Global emoji table
- PostgreSQL integration
- A myriad of various utilities
  - String and date formatting
  - `await ctx.ok()`

## Install

```sh
$ pip install git+https://github.com/slice/lifesaver
```

Documentation is available [here][docs].

[docs]: https://lifesaver.readthedocs.io/en/latest/
[jsk]: https://github.com/Gorialis/jishaku
[dpy]: https://github.com/Rapptz/discord.py
