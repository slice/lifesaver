# discord.py-lifesaver

![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)
![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Lifesaver is an opinionated Discord bot framework built on top of
[discord.py][dpy]. It aims to reduce boilerplate as much as possible and provide
common and helpful utilities that would be handy for bot developers.

> **Disclaimer:** Lifesaver was born from an attempt to package together common
> code that the author found himself duplicating throughout his bots. Therefore,
> this framework is inherently opinionated and is not intended to be consumed by
> the average bot developer.

## Features

- Built-in cogs
  - [jishaku][jsk]
  - Command error handler (`Errors`)
  - Ping and RTT (`Health`)
- Extension hot reloading via filesystem polling
- Bot (and cog) configuration primitives
- Command line module (`python -m lifesaver.cli`) for starting bots
- Global emoji table
- PostgreSQL integration
- A myraid of various utilities
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
