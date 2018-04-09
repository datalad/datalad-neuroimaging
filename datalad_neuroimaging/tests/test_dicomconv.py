
# emacs: -*- mode: python-mode; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# -*- coding: utf-8 -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Test DICOM conversion tools"""


from os.path import pardir
from os.path import dirname
from os.path import normpath
from os.path import join as opj

import datalad_neuroimaging
from datalad.api import Dataset
from datalad.api import install

from datalad.tests.utils import ok_clean_git
from datalad.tests.utils import with_tempfile
from datalad.tests.utils import assert_result_count


def get_dicom_dataset(flavor):
    modpath = dirname(datalad_neuroimaging.__file__)
    ds = install(
        dataset=normpath(opj(modpath, pardir)),
        path=opj(modpath, 'tests', 'data', 'dicoms', flavor))
    # fail on any "surprising" changes made to this dataset
    ok_clean_git(ds.path)
    return ds


@with_tempfile
def test_dicom_metadata_aggregation(path):
    dicoms = get_dicom_dataset('structural')

    ds = Dataset.create(path)
    ds.install(source=dicoms, path='acq100')
    ds.aggregate_metadata(recursive=True)
    res = ds.metadata(get_aggregates=True)
    assert_result_count(res, 2)
    assert_result_count(res, 1, path=opj(ds.path, 'acq100'))


@with_tempfile
def test_dicom2spec(path):

    # ###  SETUP ###
    dicoms = get_dicom_dataset('structural')

    ds = Dataset.create(path)
    ds.install(source=dicoms, path='acq100')
    ds.aggregate_metadata(recursive=True)
    # ### END SETUP ###

    res = ds.ni_dicom2spec(path='acq100', spec='spec_structural.json')
    assert_result_count(res, 1)
    assert_result_count(res, 1, path=opj(ds.path, 'spec_structural.json'))
