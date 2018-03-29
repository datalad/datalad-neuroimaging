# DataLad extension module template

[![Travis tests status](https://secure.travis-ci.org/datalad/datalad-module-template.png?branch=master)](https://travis-ci.org/datalad/datalad-module-template) [![codecov.io](https://codecov.io/github/datalad/datalad-module-template/coverage.svg?branch=master)](https://codecov.io/github/datalad/datalad-module-template?branch=master)

This repository contains a module template that can serve as a starting point
for implementing a [DataLad](http://datalad.org) extension. A module can
provide any number of additional DataLad commands that are automatically
included in DataLad's command line and Python API.

For a demo, clone this repository and install the demo module via

    pip install -e .

DataLad will now expose a new command suite with `hello...` commands.

    % datalad --help |grep -B2 -A2 hello
    *Demo DataLad command suite*

      hello-cmd
          Short description of the command

To start implementing your own extension module, fork this project and adjust
as necessary. The comments in [setup.py](setup.py) and
[__init__.py](dmhelloworld/__init__.py) illustrate the purpose of the various
aspects of a command implementation and the setup of an extension package. 
