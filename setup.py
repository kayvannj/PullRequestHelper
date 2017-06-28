# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='prh',
    version='2.3.1',
    url='https://github.com/kayvannj/PullRequestHelper',
    license='Apache License, Version 2.0',
    author='Kayvan Najafzadeh',
    author_email='kayvannj@gmail.com',
    description='A tool to help creating PullRequests on Github easier and automate some of the steps',
    long_description=long_description,
    install_requires=['requests'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'prh = prhpackage.__main__:main'
        ]
    }
)
