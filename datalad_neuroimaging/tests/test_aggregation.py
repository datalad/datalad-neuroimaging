# emacs: -*- mode: python-mode; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# -*- coding: utf-8 -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Test metadata aggregation"""


from datalad.distribution.dataset import Dataset
from datalad.tests.utils_pytest import (
    assert_dict_equal,
    assert_not_in,
    known_failure_osx,
    known_failure_windows,
    skip_if_adjusted_branch,
    with_tree,
)
from datalad_deprecated.metadata.metadata import Metadata

from ..extractors.tests.test_bids import bids_template


metadata = Metadata.__call__


@skip_if_adjusted_branch  # fails on crippled fs test
@known_failure_windows
@known_failure_osx
@with_tree(tree=bids_template)
def test_nested_metadata(path=None):
    ds = Dataset(path).create(force=True)
    ds.save()
    ds.aggregate_metadata()
    # BIDS returns participant info as a nested dict for each file in the
    # content metadata. On the dataset-level this should automatically
    # yield a sequence of participant info dicts, without any further action
    # or BIDS-specific configuration
    meta = metadata(
        '.', dataset=ds, reporton='datasets', return_type='item-or-list'
    )['metadata']
    for i in zip(
            sorted(
                meta['datalad_unique_content_properties']['bids']['subject'],
                key=lambda x: x['id']),
            sorted([
                {
                    "age(years)": "20-25",
                    "id": "03",
                    "gender": "female",
                    "handedness": "r",
                    "hearing_problems_current": "n",
                    "language": "english"
                },
                {
                    "age(years)": "30-35",
                    "id": "01",
                    "gender": 'n/a',
                    "handedness": "r",
                    "hearing_problems_current": "n",
                    "language": u"русский"
                }],
                key=lambda x: x['id'])):
            assert_dict_equal(i[0], i[1])
    # we can turn off this kind of auto-summary
    ds.config.add('datalad.metadata.generate-unique-bids', 'false', where='dataset')
    ds.aggregate_metadata()
    meta = ds.metadata('.', reporton='datasets', return_type='item-or-list')['metadata']
    # protect next test a little, in case we enhance our core extractor in the future
    # to provide more info
    if 'datalad_unique_content_properties' in meta:
        assert_not_in('bids', meta['datalad_unique_content_properties'])
