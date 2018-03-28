#!/usr/bin/env python

from setuptools import setup

setup(
    # basic project properties can be set arbitrarily
    name="dmhelloworld",
    author="The DataLad Team and Contributors",
    author_email="team@datalad.org",
    version='0.1',
    description="demo DataLad module package",
    # datalad command suite specs from here
    install_requires=[
        # in general datalad will be a requirement, unless the datalad extension
        # aspect is an optional component of a larger project
        'datalad',
    ],
    entry_points = {
        # 'datalad.modules' is THE entrypoint inspected by the datalad API builders
        'datalad.modules': [
            # the label in front of '=' is the command suite label
            # the entrypoint can point to any symbol of any name, as long it is
            # valid datalad interface specification (see demo in this module)
            'hello=dmhelloworld:module_suite',
        ]
    },
)
