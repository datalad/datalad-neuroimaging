
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
from datalad.tests.utils import assert_result_count
from datalad.tests.utils import ok_clean_git
from datalad.tests.utils import with_tempfile
from datalad.tests.utils import eq_

import datalad_neuroimaging
from datalad_neuroimaging.tests.utils import get_dicom_dataset
from datalad_neuroimaging.tests.utils import get_bids_dataset


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
    ds.aggregate_metadata(recursive=True, update_mode='all')
    # ### END SETUP ###

    res = ds.ni_dicom2spec(path='acq100', spec='spec_structural.json')
    assert_result_count(res, 1)
    assert_result_count(res, 1, path=opj(ds.path, 'spec_structural.json'))
    if ds.repo.is_direct_mode():
        # Note:
        # in direct mode we got an issue determining whether or not sth is
        # "dirty". In this particular case, this is about having a superdataset
        # in direct mode, while the subdataset is a plain git repo.
        # However, at least assert both are clean themselves:
        ok_clean_git(ds.path, ignore_submodules=True)
        ok_clean_git(opj(ds.path, 'acq100'))

    else:
        ok_clean_git(ds.path)


@with_tempfile
def dummy_test(path):
    # ###  SETUP ###
    session = 'sub02_acq100'  # TODO: ATM heudiconv call requires {subject}

    dicoms = get_dicom_dataset('structural')
    ds = Dataset.create(path)
    ds.install(source=dicoms, path=opj(session, 'dicoms'))
    ds.aggregate_metadata(recursive=True, update_mode='all')
    ds.ni_dicom2spec(path=opj(session, 'dicoms'),
                     spec=opj(session, 'spec_structural.json'))
    # ### END SETUP ###

    subject = session.split('_')[0]
    spec_file = opj(session, 'spec_structural.json')

    import datalad_neuroimaging.commands.cbbs_heuristic
    arg_list = ['-d', ds.path + "/{subject}_acq100/dicoms/*/*"]
    arg_list += ['-s', subject]
    arg_list += ['-c', 'dcm2niix']
    arg_list += ['-b']
    arg_list += ['-f', datalad_neuroimaging.commands.cbbs_heuristic.__file__]
    arg_list += ['-o', opj(ds.path, "converted")]

    from mock import patch
    import heudiconv.cli.run
    with patch.dict('os.environ', {'CBBS_STUDY_SPEC': opj(ds.path, spec_file)}):
        heudiconv.cli.run.main(arg_list)


def test_validate_bids_fixture():
    bids_ds = get_bids_dataset()
    # dicom source dataset is absent
    eq_(len(bids_ds.subdatasets(fulfilled=True, return_type='list')), 0)
