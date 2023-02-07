# encoding: utf-8

from os import path

from setuptools import find_packages, setup

deps = [
    "ruamel.yaml",
    "click",
    "jishaku",
    "discord.py",
    "typing_extensions",
]

setup(
    name="discord.py-lifesaver",
    version="0.0.0",
    author="slice",
    license="MIT",
    keywords="discord discord.py",
    description=(
        "An opinionated bot framework, foundation, and utility library "
        "for Discord.py. Aims to reduce boilerplate."
    ),
    url="https://github.com/slice/lifesaver",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    package_data={"lifesaver": ["py.typed"]},
    python_requires=">=3.7",
    packages=find_packages(),
    install_requires=deps,
    extras_require={
        "docs": [
            "sphinx==1.8.1",
            "sphinxcontrib-napoleon==0.7",
            "sphinxcontrib-asyncio==0.2.0",
        ],
    },
    zip_safe=False,
)
