#!/usr/bin/env python

from setuptools import setup
from setuptools import findall

from os.path import join as opj
from os.path import sep as pathsep
from os.path import splitext

from _datalad_buildsupport.setup import (
    BuildManPage,
    BuildRSTExamplesFromScripts,
)

import versioneer


def findsome(subdir, extensions):
    """Find files under subdir having specified extensions

    Leading directory (datalad) gets stripped
    """
    return [
        f.split(pathsep, 1)[1] for f in findall(opj('datalad_neuroimaging', subdir))
        if splitext(f)[-1].lstrip('.') in extensions
    ]


cmdclass = {
    'build_manpage': BuildManPage,
    'build_examples': BuildRSTExamplesFromScripts,
}


setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(cmdclass),
    package_data={
        'datalad_neuroimaging':
            findsome(opj('tests', 'data', 'files'), {'dcm', 'gz'}) +
            findsome('resources', {'py', 'txt'})},
)
