import os
from json import load
from setuptools import setup, find_packages

# Load module info
with open((os.path.join(os.path.dirname(__file__), 'pkg_info.json'))) as info:
    _info = load(info)

setup(
    name='User cabinet',
    version=_info['version'],
    description='Epam final project',
    platforms='win32, linux',
    author=_info['author'],
    author_email=_info['author_email'],
    zip_safe=False,
    url=_info['url'],
    packages=find_packages(),
)
