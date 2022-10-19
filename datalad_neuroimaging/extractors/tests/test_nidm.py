# emacs: -*- mode: python-mode; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Test NIDM extractor"""

from os.path import dirname
from os.path import join as opj
from shutil import copy

from datalad.api import Dataset
from datalad.tests.utils_pytest import (
    assert_result_count,
    assert_status,
    known_failure_osx,
    known_failure_windows,
    ok_clean_git,
    skip_if_adjusted_branch,
    with_tempfile,
)

from . import datalad_extracts_annex_key


@skip_if_adjusted_branch  # fails on crippled fs test
@known_failure_windows
@known_failure_osx
@with_tempfile(mkdir=True)
def test_nidm(path=None):
    ds = Dataset(path).create()
    ds.config.add('datalad.metadata.nativetype', 'nidm', where='dataset')
    # imagine filling the dataset up with something that NIDM info could be
    copy(
        opj(dirname(dirname(dirname(__file__))), 'tests', 'data', 'files', 'nifti1.nii.gz'),
        path)
    # extracted from
    ds.save()
    # all nice and tidy, nothing untracked
    ok_clean_git(ds.path)
    # engage the extractor(s)
    res = ds.aggregate_metadata()
    # aggregation done without whining
    assert_status('ok', res)
    res = ds.metadata(reporton='datasets')
    # ATM we do not forsee file-based metadata to come back from NIDM
    assert_result_count(res, 1)
    # kill version info
    core = res[0]['metadata']['datalad_core']
    core.pop('version', None)
    core.pop('refcommit')
    # show full structure of the assembled metadata from demo content
    target_metadata = {
        "@context": {"@vocab": "http://docs.datalad.org/schema_v2.0.json"},
        "datalad_core": {"@id": ds.id}, "nidm": {
            "@context": {"mydurationkey": {"@id": "time:Duration"},
                         "myvocabprefix": {
                             "@id": "http://purl.org/ontology/mydefinition",
                             "description": "I am a vocabulary",
                             "type":
                                 "http://purl.org/dc/dcam/VocabularyEncodingScheme"}},
            "mydurationkey": 0.6}}

    if datalad_extracts_annex_key:
        target_metadata['datalad_unique_content_properties'] = \
            {
                "annex": {
                 "key": [
                  "MD5E-s15920--acfb708aa74951cfff1a9d466f6d77be.nii.gz"
                 ]
                }
            }

    assert_result_count(res, 1, metadata=target_metadata)
