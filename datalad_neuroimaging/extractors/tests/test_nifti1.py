# emacs: -*- mode: python-mode; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Test NIfTI extractor"""

from datalad.tests.utils_pytest import SkipTest

try:
    import nibabel
except ImportError:
    raise SkipTest

from os.path import dirname
from os.path import join as opj
from shutil import copy

from datalad.api import Dataset
from datalad.tests.utils_pytest import (
    assert_in,
    assert_result_count,
    assert_status,
    eq_,
    known_failure_osx,
    known_failure_windows,
    ok_clean_git,
    skip_if_adjusted_branch,
    with_tempfile,
)

target = {
    "description": "FSL5.0",
    "spatial_resolution(mm)": [2.0, 2.0, 2.0],
    "temporal_spacing(s)": 6.0,
    "datatype": "int16",
    "dim": [4, 91, 109, 91, 2, 1, 1, 1],
    "pixdim": [-1.0, 2.0, 2.0, 2.0, 6.0, 1.0, 1.0, 1.0],
    "xyz_unit": "millimeter (uo:0000016)",
    "t_unit": "second (uo:0000010)",
    "cal_min": 3000.0,
    "cal_max": 8000.0,
    "toffset": 0.0,
    "vox_offset": 0.0,
    "intent": "none",
    "sizeof_hdr": 348,
    "magic": "n+1",
    "sform_code": "mni",
    "qform_code": "mni",
    "freq_axis": None,
    "phase_axis": None,
    "slice_axis": None,
    "slice_start": 0,
    "slice_duration": 0.0,
    "slice_order": "unknown",
    "slice_end": 0,
}


@skip_if_adjusted_branch  # fails on crippled fs test
@known_failure_windows
@known_failure_osx
@with_tempfile(mkdir=True)
def test_nifti(path=None):
    ds = Dataset(path).create()
    ds.config.add('datalad.metadata.nativetype', 'nifti1', where='dataset')
    copy(
        opj(dirname(dirname(dirname(__file__))), 'tests', 'data', 'files', 'nifti1.nii.gz'),
        path)
    ds.save()
    ok_clean_git(ds.path)
    res = ds.aggregate_metadata()
    assert_status('ok', res)
    res = ds.metadata('nifti1.nii.gz')
    assert_result_count(res, 1)

    # from this extractor
    meta = res[0]['metadata']['nifti1']
    for k, v in target.items():
        eq_(meta[k], v)

    assert_in('@context', meta)
