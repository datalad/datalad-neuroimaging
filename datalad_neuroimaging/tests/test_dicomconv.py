
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

from os.path import join as opj

from datalad.api import Dataset
from datalad.tests.utils_pytest import assert_result_count
from datalad.tests.utils_pytest import ok_clean_git
from datalad.tests.utils_pytest import with_tempfile
from datalad.tests.utils_pytest import eq_
from datalad.tests.utils_pytest import known_failure_osx
from datalad.tests.utils_pytest import known_failure_windows
from datalad.tests.utils_pytest import skip_if_adjusted_branch


import datalad_neuroimaging
from datalad_neuroimaging.tests.utils import get_dicom_dataset
from datalad_neuroimaging.tests.utils import get_bids_dataset


@known_failure_windows
@known_failure_osx
@with_tempfile
def test_dicom_metadata_aggregation(path=None):
    dicoms = get_dicom_dataset('structural')

    ds = Dataset.create(path)
    ds.install(source=dicoms, path='acq100')
    ds.aggregate_metadata(recursive=True)
    res = ds.metadata(get_aggregates=True)
    assert_result_count(res, 2)
    assert_result_count(res, 1, path=opj(ds.path, 'acq100'))


@skip_if_adjusted_branch
@known_failure_windows
@known_failure_osx
def test_validate_bids_fixture():
    bids_ds = get_bids_dataset()
    # dicom source dataset is absent
    eq_(len(bids_ds.subdatasets(fulfilled=True, return_type='list')), 0)
