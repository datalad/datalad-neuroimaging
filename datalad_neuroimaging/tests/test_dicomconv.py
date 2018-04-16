
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

import datalad_neuroimaging
from datalad_neuroimaging.tests.utils import get_dicom_dataset


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

    # TODO: heudiconv is (at least locally) currently failing. However,
    # sub-sub02_ses-anatT1w_task-anatT1w_run-1_bold.nii.gz (and *.json)
    # was created:

    # INFO: stdout 2018-04-16T11:41:14.576055:Conversion required 4.175391 seconds (4.174333 for core code).
    # INFO: [Node] Finished "convert".
    # Traceback (most recent call last):
    #   File "/home/ben/cbbs_imaging/datalad-neuroimaging/venv/bin/heudiconv", line 11, in <module>
    #     load_entry_point('heudiconv', 'console_scripts', 'heudiconv')()
    #   File "/home/ben/cbbs_imaging/heudiconv/heudiconv/cli/run.py", line 120, in main
    #     process_args(args)
    #   File "/home/ben/cbbs_imaging/heudiconv/heudiconv/cli/run.py", line 330, in process_args
    #     overwrite=args.overwrite,)
    #   File "/home/ben/cbbs_imaging/heudiconv/heudiconv/convert.py", line 194, in prep_conversion
    #     overwrite=overwrite,)
    #   File "/home/ben/cbbs_imaging/heudiconv/heudiconv/convert.py", line 288, in convert
    #     save_scans_key(item, bids_outfiles)
    #   File "/home/ben/cbbs_imaging/heudiconv/heudiconv/bids.py", line 212, in save_scans_key
    #     rows[f_name] = get_formatted_scans_key_row(item)
    #   File "/home/ben/cbbs_imaging/heudiconv/heudiconv/bids.py", line 296, in get_formatted_scans_key_row
    #     date = mw.dcm_data.ContentDate
    #   File "/home/ben/cbbs_imaging/datalad-neuroimaging/venv/lib/python3.5/site-packages/dicom/dataset.py", line 257, in __getattr__
    #     "'{0:s}'.".format(name))
    # AttributeError: Dataset does not have attribute 'ContentDate'.



