# discord.py-lifesaver

![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)
![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Lifesaver is an opinionated Discord bot framework built on top of
[discord.py][dpy]. It exports an assortment of utilities and helpers that ease
the burden of maintenance when it comes to everyday botmaking, and it's
especially handy to those who maintain multiple bots at a time.

> **Warning**: Lifesaver's raison d'être is code deduplication. It's not
> inherently useful to everyone.

## Features

- Built-in cogs
  - [jishaku][jsk]
  - Command error handler (`Errors`)
  - Ping (`Health`)
- Extension hot reloading via filesystem polling
- Bot (and cog) configuration primitives via YAML
- Command line module (`python -m lifesaver.cli`) for bootstraping bots
- Global emoji table
- PostgreSQL integration
- A cornucopia of diverse utilities
  - Strings, dates, and escaping
  - Localization
  - `await ctx.ok()`
  - `await ctx.pick_from_list()`
  - and more...

## Install

Installation via pip (not recommended; Nix preferred):

```sh
$ pip install git+https://github.com/slice/lifesaver
```

Documentation is available [here][docs] and is provided on a best-effort basis
(sorry).

[docs]: https://lifesaver.readthedocs.io/en/latest/
[jsk]: https://github.com/Gorialis/jishaku
[dpy]: https://github.com/Rapptz/discord.py
