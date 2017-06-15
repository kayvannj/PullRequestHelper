from setuptools import setup, find_packages

setup(
    name='prhpackage',
    version='2.3.0',
    url='https://github.com/kayvannj/PullRequestHelper',
    license='Apache License, Version 2.0',
    author='Kayvan Najafzadeh',
    author_email='kayvannj@gmail.com',
    description='A tool to help creating PullRequests on Github easier and automate some of the steps',
    install_requires=['requests'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'prh = prhpackage.__main__:main'
        ]
    }
)
