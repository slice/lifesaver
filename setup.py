# encoding: utf-8

from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name='discord.py-lifesaver',
    version='0.0.0',
    keywords='discord bot framework discord.py',
    description=('Lifesaver is an extremely opinionated bot foundation that provides a bunch of '
                 'handy utilities to the average Discord.py developer.'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/slice/discord.py-lifesaver',
    author='slice',
    author_email='ryaneft@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    python_requires='>=3.6',
    packages=find_packages(),
    install_requires=[
        'ruamel.yaml',
        'click',
        'jishaku',
        'discord.py @ git+https://github.com/Rapptz/discord.py.git@rewrite',
    ],
    extras_require={
        'docs': [
            'sphinx==1.8.1',
            'sphinxcontrib-napoleon==0.7',
            'sphinxcontrib-asyncio==0.2.0',
        ],
    },
)
