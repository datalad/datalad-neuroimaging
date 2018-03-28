#!/usr/bin/env python

from setuptools import setup

setup(
    name="dmhelloworld",
    author="The DataLad Team and Contributors",
    author_email="team@datalad.org",
    version='0.1',
    description="demo DataLad module package",
    install_requires=[
        'datalad',
    ],
    entry_points = {
        'datalad.modules': [
            'hello=dmhelloworld:module_suite',
        ]
    },
)
