# -*- encoding: utf-8 -*-
"""
Python setup file.

In order to register your app at pypi.python.org, create an account at
pypi.python.org and login, then register your new app like so:

    python setup.py register

If your name is still free, you can now make your first release but first you
should check if you are uploading the correct files:

    python setup.py sdist

Inspect the output thoroughly. There shouldn't be any temp files and if your
app includes staticfiles or templates, make sure that they appear in the list.
If something is wrong, you need to edit MANIFEST.in and run the command again.

If all looks good, you can make your first release:

    python setup.py sdist upload

For new releases, you need to bump the version number in
tornado_botocore/__init__.py and re-run the above command.

For more information on creating source distributions, see
http://docs.python.org/2/distutils/sourcedist.html

"""
import os

from setuptools import setup, find_packages


def read(file_name):
    try:
        return open(os.path.join(os.path.dirname(__file__), file_name)).read()
    except IOError:
        return ''


setup(
    name="aiobittrex",
    version='0.0.2',
    description="Async Bittrex api wrapper.",
    long_description=read('README.rst'),
    license='The MIT License',
    platforms=['OS Independent'],
    keywords='async, bittrex',
    author='Oleksandr Polieno',
    author_email='polyenoom@gmail.com',
    url="https://github.com/nanvel/aiobittrex",
    packages=find_packages(),
    package_data={'': ['requirements.txt']},
    include_package_data=True,
    install_requires=[
        'aiohttp'
    ]
)
