
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
from datalad.tests.utils_pytest import (
    assert_result_count,
    eq_,
    known_failure_osx,
    known_failure_windows,
    ok_clean_git,
    skip_if_adjusted_branch,
    with_tempfile,
)

import datalad_neuroimaging
from datalad_deprecated.metadata.aggregate import AggregateMetaData
from datalad_deprecated.metadata.metadata import Metadata
from datalad_neuroimaging.tests.utils import (
    get_bids_dataset,
    get_dicom_dataset,
)


aggregate_metadata = AggregateMetaData.__call__
metadata = Metadata.__call__


@known_failure_windows
@known_failure_osx
@with_tempfile
def test_dicom_metadata_aggregation(path=None):
    dicoms = get_dicom_dataset('structural')

    ds = Dataset.create(path)
    ds.install(source=dicoms, path='acq100')
    aggregate_metadata(dataset=ds, recursive=True)
    res = metadata(dataset=ds, get_aggregates=True)
    assert_result_count(res, 2)
    assert_result_count(res, 1, path=opj(ds.path, 'acq100'))


@skip_if_adjusted_branch
@known_failure_windows
@known_failure_osx
def test_validate_bids_fixture():
    bids_ds = get_bids_dataset()
    # dicom source dataset is absent
    # yoh: disabled since makes little sense (now?) since dataset is subdataset
    # as of 978772e9468a5ae30de309cc6ac4370795de75cc etc in 2018
    # eq_(len(bids_ds.subdatasets(fulfilled=True, return_type='list')), 0)
