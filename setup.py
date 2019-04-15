#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages
from setuptools import findall

from os.path import join as opj
from os.path import sep as pathsep
from os.path import splitext
from os.path import dirname

from setup_support import BuildManPage
from setup_support import BuildRSTExamplesFromScripts
from setup_support import get_version


def findsome(subdir, extensions):
    """Find files under subdir having specified extensions

    Leading directory (datalad) gets stripped
    """
    return [
        f.split(pathsep, 1)[1] for f in findall(opj('datalad_neuroimaging', subdir))
        if splitext(f)[-1].lstrip('.') in extensions
    ]

# extension version
version = get_version()

cmdclass = {
    'build_manpage': BuildManPage,
    'build_examples': BuildRSTExamplesFromScripts,
}

# PyPI doesn't render markdown yet. Workaround for a sane appearance
# https://github.com/pypa/pypi-legacy/issues/148#issuecomment-227757822
README = opj(dirname(__file__), 'README.md')
try:
    import pypandoc
    long_description = pypandoc.convert(README, 'rst')
except (ImportError, OSError) as exc:
    # attempting to install pandoc via brew on OSX currently hangs and
    # pypandoc imports but throws OSError demanding pandoc
    print(
        "WARNING: pypandoc failed to import or thrown an error while converting"
        " README.md to RST: %r   .md version will be used as is" % exc
    )
    long_description = open(README).read()


setup(
    # basic project properties can be set arbitrarily
    name="datalad_neuroimaging",
    author="The DataLad Team and Contributors",
    author_email="team@datalad.org",
    version=version,
    description="DataLad extension package for neuro/medical imaging",
    long_description=long_description,
    packages=[pkg for pkg in find_packages('.') if pkg.startswith('datalad')],
    # datalad command suite specs from here
    install_requires=[
        'datalad[full]>=0.10.0.rc1',
        #'datalad-webapp',
        'pydicom',  # DICOM metadata
        'pybids>=0.7.0',  # BIDS metadata
        'nibabel',  # NIfTI metadata
        'pandas',  # bids2scidata export
    ],
    extras_require={
        'devel-docs': [
            # used for converting README.md -> .rst for long_description
            'pypandoc',
            # Documentation
            'sphinx',
            'sphinx-rtd-theme',
        ]},
    cmdclass=cmdclass,
    package_data={
        'datalad_neuroimaging':
            findsome(opj('tests', 'data', 'files'), {'dcm', 'gz'}) +
            findsome('resources', {'txt'})},
    entry_points = {
        # 'datalad.extensions' is THE entrypoint inspected by the datalad API builders
        'datalad.extensions': [
            # the label in front of '=' is the command suite label
            # the entrypoint can point to any symbol of any name, as long it is
            # valid datalad interface specification (see demo in this extension)
            'neuroimaging=datalad_neuroimaging:command_suite',
        ],
        'datalad.webapps': [
            'pork=webapp.app:Pork',
        ],
        'datalad.metadata.extractors': [
            'bids=datalad_neuroimaging.extractors.bids:MetadataExtractor',
            'dicom=datalad_neuroimaging.extractors.dicom:MetadataExtractor',
            'nidm=datalad_neuroimaging.extractors.nidm:MetadataExtractor',
            'nifti1=datalad_neuroimaging.extractors.nifti1:MetadataExtractor',
            'minc=datalad_neuroimaging.extractors.minc:MetadataExtractor',
        ],
        'datalad.tests': [
            'neuroimaging=datalad_neuroimaging',
        ],
    },
)
