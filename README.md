     ____          _           _                 _
    |  _ \   __ _ | |_   __ _ | |      __ _   __| |
    | | | | / _` || __| / _` || |     / _` | / _` |
    | |_| || (_| || |_ | (_| || |___ | (_| || (_| |
    |____/  \__,_| \__| \__,_||_____| \__,_| \__,_|
                                       Neuroimaging

[![Travis tests status](https://secure.travis-ci.org/datalad/datalad-neuroimaging.png?branch=master)](https://travis-ci.org/datalad/datalad-neuroimaging) [![codecov.io](https://codecov.io/github/datalad/datalad-neuroimaging/coverage.svg?branch=master)](https://codecov.io/github/datalad/datalad-neuroimaging?branch=master) [![Documentation](https://readthedocs.org/projects/datalad-neuroimaging/badge/?version=latest)](http://datalad-neuroimaging.rtfd.org) [![https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg](https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg)](https://singularity-hub.org/collections/841) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![GitHub release](https://img.shields.io/github/release/datalad/datalad-neuroimaging.svg)](https://GitHub.com/datalad/datalad-neuroimaging/releases/) [![PyPI version fury.io](https://badge.fury.io/py/datalad-neuroimaging.svg)](https://pypi.python.org/pypi/datalad-neuroimaging/) [![Average time to resolve an issue](http://isitmaintained.com/badge/resolution/datalad/datalad-neuroimaging.svg)](http://isitmaintained.com/project/datalad/datalad-neuroimaging "Average time to resolve an issue") [![Percentage of issues still open](http://isitmaintained.com/badge/open/datalad/datalad-neuroimaging.svg)](http://isitmaintained.com/project/datalad/datalad-neuroimaging "Percentage of issues still open")

This extension enhances DataLad (http://datalad.org) for working with
neuroimaging data and workflows. Please see the [extension
documentation](http://datalad-neuroimaging.rtfd.org)
for a description on additional commands and functionality.

For general information on how to use or contribute to DataLad (and this
extension), please see the [DataLad website](http://datalad.org) or the
[main GitHub project page](http://datalad.org).


## Installation

Before you install this package, please make sure that you [install a recent
version of git-annex](https://git-annex.branchable.com/install).  Afterwards,
install the latest version of `datalad-neuroimaging` from
[PyPi](https://pypi.org/project/datalad-neuroimaging). It is recommended to use
a dedicated [virtualenv](https://virtualenv.pypa.io):

    # create and enter a new virtual environment (optional)
    virtualenv --system-site-packages --python=python3 ~/env/dataladni
    . ~/env/dataladni/bin/activate

    # install from PyPi
    pip install datalad_neuroimaging

There is also a [Singularity container](http://singularity.lbl.gov) available.
The latest release version can be obtained by running:

    singularity pull shub://datalad/datalad-neuroimaging


## Acknowledgements

DataLad development is supported by a US-German collaboration in
computational neuroscience (CRCNS) project "DataGit: converging catalogues,
warehouses, and deployment logistics into a federated 'data distribution'"
(Halchenko/Hanke), co-funded by the US National Science Foundation (NSF
1429999) and the German Federal Ministry of Education and Research (BMBF
01GQ1411). Additional support is provided by the German federal state of
Saxony-Anhalt and the European Regional Development
Fund (ERDF), Project: Center for Behavioral Brain Sciences, Imaging Platform
