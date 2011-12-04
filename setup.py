#!/usr/bin/env python

import sys

from setuptools import setup, find_packages


long_description = open('README').read()

setup(
    name='drbd_creator',
    version='0.1',
    description='drbd_creator is a simple tool for creating DRBD resource over LVM logical volume.',
    long_description=long_description,
    author='Lipin Dmitriy',
    author_email='blackwithwhite666@gmail.com',
    url='https://github.com/blackwithwhite666/drbd_creator',
    packages=find_packages(),
    install_requires=['paramiko', 'ply'],
    entry_points={
        'console_scripts': [
            'create-drbd = drbd_creator.cli:main',
        ]
    },
    classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Operating System :: Linux',
          'Programming Language :: Python',
          'Topic :: System :: Clustering',
          'Topic :: System :: Systems Administration',
    ],
)