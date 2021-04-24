from setuptools import setup
from setuptools import find_packages

setup(
    name='User cabinet',
    version='0.1.1',
    description='Epam final project',
    platforms=['win32, linux'],
    author='Krytskyi Anton',
    author_email='mujanjagusav@gmail.com',
    zip_safe=False,
    url='https://github.com/antkrit/project.git',
    packages=find_packages(),
)
