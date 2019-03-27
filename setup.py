# encoding: utf-8

from os import path
from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

deps = [
    'ruamel.yaml',
    'click',
    'jishaku',
    'discord.py >= 1.0.0a1767',
]

setup(
    name='discord.py-lifesaver',
    version='0.0.0',
    author='slice',
    license='MIT',
    keywords='discord discord.py',
    description=(
        'An opinionated bot framework, foundation, and utility library '
        'for Discord.py. Aims to reduce boilerplate.'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/slice/lifesaver',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    python_requires='>=3.7',
    packages=find_packages(),
    install_requires=deps,
    extras_require={
        'docs': [
            'sphinx==1.8.1',
            'sphinxcontrib-napoleon==0.7',
            'sphinxcontrib-asyncio==0.2.0',
        ],
    },
)
