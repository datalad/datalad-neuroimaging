from os.path import dirname, normpath, join as opj, pardir

from datalad.api import Dataset
from datalad.coreapi import install
from datalad.tests.utils import ok_clean_git
from datalad.tests.utils import with_tempfile

import datalad_neuroimaging


def get_dicom_dataset(flavor):
    modpath = dirname(datalad_neuroimaging.__file__)
    ds = install(
        dataset=normpath(opj(modpath, pardir)),
        path=opj(modpath, 'tests', 'data', 'dicoms', flavor))
    # fail on any "surprising" changes made to this dataset
    ok_clean_git(ds.path)
    return ds


def create_dicom_tarball(flavor, path):
    import tarfile
    ds = get_dicom_dataset(flavor=flavor)
    with tarfile.open(path, "w:gz") as tar:
        tar.add(ds.path)
    return path
