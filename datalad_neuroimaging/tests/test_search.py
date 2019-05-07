# emacs: -*- mode: python-mode; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# -*- coding: utf-8 -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Some additional tests for search command"""
import os

from difflib import unified_diff
from shutil import copy
from os import makedirs
from os.path import join as opj
from os.path import dirname
from datalad.utils import swallow_outputs
from datalad.tests.utils import assert_in
from datalad.tests.utils import assert_equal
from datalad.tests.utils import assert_result_count
from datalad.tests.utils import with_tempfile
from datalad.tests.utils import with_tree
from datalad.tests.utils import ok_clean_git
from datalad.tests.utils import SkipTest
from datalad.tests.utils import skip_if

from datalad.api import Dataset
from datalad.api import search
from datalad.metadata import search as search_mod
try:
    from datalad_neuroimaging.extractors.tests.test_bids import bids_template
except (ImportError, SkipTest):
    # pybids might be absent which would preclude this import
    bids_template = None


@with_tempfile
def test_our_metadataset_search(tdir):
    # TODO renable when a dataset with new aggregated metadata is
    # available at some public location
    raise SkipTest
    # smoke test for basic search operations on our super-megadataset
    # expensive operation but ok
    #ds = install(
    #    path=tdir,
    #    # TODO renable test when /// metadata actually conforms to the new metadata
    #    #source="///",
    #    source="smaug:/mnt/btrfs/datasets-meta6-4/datalad/crawl",
    #    result_xfm='datasets', return_type='item-or-list')
    assert list(ds.search('haxby'))
    assert_result_count(
        ds.search('id:873a6eae-7ae6-11e6-a6c8-002590f97d84', mode='textblob'),
        1,
        type='dataset',
        path=opj(ds.path, 'crcns', 'pfc-2'))

    # there is a problem with argparse not decoding into utf8 in PY2
    from datalad.cmdline.tests.test_main import run_main
    # TODO: make it into an independent lean test
    from datalad.cmd import Runner
    out, err = Runner(cwd=ds.path)('datalad search Buzsáki')
    assert_in('crcns/pfc-2 ', out)  # has it in description
    # and then another aspect: this entry it among multiple authors, need to
    # check if aggregating them into a searchable entity was done correctly
    assert_in('crcns/hc-1 ', out)


@skip_if(not bids_template, "No bids_template (probably no pybids installed)")
@with_tree(bids_template)
def test_within_ds_file_search(path):
    try:
        import nibabel
    except ImportError:
        raise SkipTest
    ds = Dataset(path).create(force=True)
    ds.config.add('datalad.metadata.nativetype', 'nifti1', where='dataset')
    makedirs(opj(path, 'stim'))
    for src, dst in (
            ('nifti1.nii.gz', opj('sub-01', 'func', 'sub-01_task-some_bold.nii.gz')),
            ('nifti1.nii.gz', opj('sub-03', 'func', 'sub-03_task-other_bold.nii.gz'))):
        copy(
            opj(dirname(dirname(__file__)), 'tests', 'data', 'files', src),
            opj(path, dst))
    ds.add('.')
    ds.aggregate_metadata()
    ok_clean_git(ds.path)
    # basic sanity check on the metadata structure of the dataset
    dsmeta = ds.metadata('.', reporton='datasets')[0]['metadata']
    for src in ('bids', 'nifti1'):
        # something for each one
        assert_in(src, dsmeta)
        # each src declares its own context
        assert_in('@context', dsmeta[src])
        # we have a unique content metadata summary for each src
        assert_in(src, dsmeta['datalad_unique_content_properties'])

    # test default behavior
    with swallow_outputs() as cmo:
        ds.search(show_keys='name', mode='textblob')

        assert_in("""\
id
meta
parentds
path
type
""", cmo.out)

    target_out = """\
annex.key
bids.BIDSVersion
bids.author
bids.citation
bids.conformsto
bids.datatype
bids.description
bids.fundedby
bids.license
bids.name
bids.subject.age(years)
bids.subject.gender
bids.subject.handedness
bids.subject.hearing_problems_current
bids.subject.id
bids.subject.language
bids.suffix
bids.task
datalad_core.id
datalad_core.refcommit
id
nifti1.cal_max
nifti1.cal_min
nifti1.datatype
nifti1.description
nifti1.dim
nifti1.freq_axis
nifti1.intent
nifti1.magic
nifti1.phase_axis
nifti1.pixdim
nifti1.qform_code
nifti1.sform_code
nifti1.sizeof_hdr
nifti1.slice_axis
nifti1.slice_duration
nifti1.slice_end
nifti1.slice_order
nifti1.slice_start
nifti1.spatial_resolution(mm)
nifti1.t_unit
nifti1.temporal_spacing(s)
nifti1.toffset
nifti1.vox_offset
nifti1.xyz_unit
parentds
path
type
"""

    # check generated autofield index keys
    with swallow_outputs() as cmo:
        ds.search(mode='autofield', show_keys='name')
        # it is impossible to assess what is different from that dump
        # so we will use diff
        diff = list(unified_diff(target_out.splitlines(), cmo.out.splitlines()))
        assert_in(target_out, cmo.out, msg="Diff: %s" % os.linesep.join(diff))

    assert_result_count(ds.search('blablob#'), 0)
    # now check that we can discover things from the aggregated metadata
    for mode, query, hitpath, matched_key, matched_val in (
            # random keyword query
            # multi word query implies AND
            ('textblob',
             ['bold', 'female'],
             opj('sub-03', 'func', 'sub-03_task-some_bold.nii.gz'),
             'meta', 'female'),
            # report which field matched with auto-field
            ('autofield',
             'female',
             opj('sub-03', 'func', 'sub-03_task-other_bold.nii.gz'),
             'bids.subject.gender', 'female'),
            # autofield multi-word query is also AND
            ('autofield',
             ['bids.suffix:bold', 'bids.subject.id:01'],
             opj('sub-01', 'func', 'sub-01_task-some_bold.nii.gz'),
             'bids.suffix', 'bold'),
            # TODO extend with more complex queries to test whoosh
            # query language configuration
    ):
        res = ds.search(query, mode=mode, full_record=True)
        if mode == 'textblob':
            # 'textblob' does datasets by default only (be could be configured otherwise
            assert_result_count(res, 1)
        else:
            # the rest has always a file and the dataset, because they carry metadata in
            # the same structure
            assert_result_count(res, 2)
            assert_result_count(
                res, 1, type='file', path=opj(ds.path, hitpath),
                # each file must report the ID of the dataset it is from, critical for
                # discovering related content
                dsid=ds.id)
        assert_result_count(
            res, 1, type='dataset', path=ds.path, dsid=ds.id)
        # test the key and specific value of the match
        assert_in(matched_key, res[-1]['query_matched'])
        assert_equal(res[-1]['query_matched'][matched_key], matched_val)
