#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages

setup(
    # basic project properties can be set arbitrarily
    name="datalad_neuroimaging",
    author="The DataLad Team and Contributors",
    author_email="team@datalad.org",
    version='0.1',
    description="DataLad extension package for neuro/medical imaging",
    packages=[pkg for pkg in find_packages('.') if pkg.startswith('datalad')],
    # datalad command suite specs from here
    install_requires=[
        # in general datalad will be a requirement, unless the datalad extension
        # aspect is an optional component of a larger project
        # for now we need git snapshots (requirements.txt)
        #'datalad',
        #'datalad-webapp',
        'pydicom',  # DICOM metadata
        'pybids>=0.5.1',  # BIDS metadata
        'nibabel',  # NIfTI metadata
        'pandas',  # bids2scidata export
    ],
    package_data={
        'datalad_neuroimaging':
            findsome(opj('tests', 'data'), {'dcm', 'gz'})},
    entry_points = {
        # 'datalad.modules' is THE entrypoint inspected by the datalad API builders
        'datalad.modules': [
            # the label in front of '=' is the command suite label
            # the entrypoint can point to any symbol of any name, as long it is
            # valid datalad interface specification (see demo in this module)
            'neuroimaging=datalad_helloworld:module_suite',
        ],
        'datalad.webapps': [
            'pork=webapp.app:Pork',
        ],
        'datalad.metadata.extractors': [
            'bids=datalad.metadata.extractors.bids:MetadataExtractor',
            'dicom=datalad.metadata.extractors.dicom:MetadataExtractor',
            'nidm=datalad.metadata.extractors.nidm:MetadataExtractor',
            'nifti1=datalad.metadata.extractors.nifti1:MetadataExtractor',
        ],
    },
)
