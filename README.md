# discord.py-lifesaver

![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)
![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)

Lifesaver is an opinionated bot framework, foundation, and utility library
built on top of [discord.py][dpy]. It aims to reduce boilerplate and implement
common features and utilities that would be handy for the common bot.

> **Disclaimer:** Lifesaver was born from an attempt to package together common
> code that the author found himself duplicating throughout his bots.
> Therefore, this framework is inherently opinionated and is not intended to be
> consumed by the average bot developer.

## Features

* [jishaku][jsk] built in
* Hot reloading via filesystem polling
* Command line interface for starting bots
* Bot configuration primitives
  * Per-cog configuration as well
* Various formatting utilities

## Install

```sh
$ pip install git+https://github.com/slice/lifesaver
```

Documentation is available [here][docs].

[docs]: https://lifesaver.readthedocs.io/en/latest/
[jsk]: https://github.com/Gorialis/jishaku
[dpy]: https://github.com/Rapptz/discord.py
