# emacs: -*- mode: python-mode; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Test BIDS-dataset metadata extractor """
import json
from math import isnan
from os.path import join as opj

from datalad.api import Dataset
from datalad.support.external_versions import external_versions
from datalad.tests.utils_pytest import (
    assert_equal,
    assert_in,
    known_failure_osx,
    known_failure_windows,
    skip_if_no_module,
    with_tree,
)

skip_if_no_module('bids')

from unittest import TestCase

from datalad_neuroimaging.extractors.bids_dataset import BIDSmeta

TestCase.maxDiff = None

bids_template = {
    '.datalad': {
        'config': '[datalad "metadata"]\n  nativetype = bids',},
    'dataset_description.json': """
{
    "Name": "The mother of all experiments",
    "BIDSVersion": "1.4.0",
    "DatasetType": "raw",
    "License": "CC0",
    "Authors": [
        "Paul Broca",
        "Carl Wernicke"
    ],
    "Acknowledgements": "Special thanks to Korbinian Brodmann for help in formatting this dataset in BIDS. We thank Alan Lloyd Hodgkin and Andrew Huxley for helpful comments and discussions about the experiment and manuscript; Hermann Ludwig Helmholtz for administrative support; and Claudius Galenus for providing data for the medial-to-lateral index analysis.",
    "HowToAcknowledge": "Please cite this paper: https://www.ncbi.nlm.nih.gov/pubmed/001012092119281",
    "Funding": [
        "National Institute of Neuroscience Grant F378236MFH1",
        "National Institute of Neuroscience Grant 5RMZ0023106"
    ],
    "EthicsApprovals": [
        "Army Human Research Protections Office (Protocol ARL-20098-10051, ARL 12-040, and ARL 12-041)"
    ],
    "ReferencesAndLinks": [
        "https://www.ncbi.nlm.nih.gov/pubmed/001012092119281",
        "Alzheimer A., & Kraepelin, E. (2015). Neural correlates of presenile dementia in humans. Journal of Neuroscientific Data, 2, 234001. doi:1920.8/jndata.2015.7"
    ],
    "DatasetDOI": "doi:10.0.2.3/dfjj.10",
    "HEDVersion": "7.1.1"
}
""",
    'participants.tsv': u"""\
participant_id\tgender\tage\thandedness\thearing_problems_current\tlanguage
sub-01\tn/a\t30-35\tr\tn\tрусский
sub-03\tf\t20-25\tr\tn\tenglish
""",
    'README.md': """
A very detailed description с юникодом
""",
    'sub-01': {'func': {'sub-01_task-some_bold.nii.gz': ''}},
    'sub-03': {'func': {'sub-03_task-other_bold.nii.gz': ''}},
    'derivatives': {'empty': {}}  # Test that we do not blow if derivatives present
}

correct_metadata = """\
{
    "Acknowledgements": "Special thanks to Korbinian Brodmann for help in formatting this dataset in BIDS. We thank Alan Lloyd Hodgkin and Andrew Huxley for helpful comments and discussions about the experiment and manuscript; Hermann Ludwig Helmholtz for administrative support; and Claudius Galenus for providing data for the medial-to-lateral index analysis.",
    "Authors": [
        "Carl Wernicke",
        "Paul Broca"
    ],
    "BIDSVersion": "1.4.0",
    "DatasetDOI": "doi:10.0.2.3/dfjj.10",
    "DatasetType": "raw",
    "EthicsApprovals": [
        "Army Human Research Protections Office (Protocol ARL-20098-10051, ARL 12-040, and ARL 12-041)"
    ],
    "Funding": [
        "National Institute of Neuroscience Grant 5RMZ0023106",
        "National Institute of Neuroscience Grant F378236MFH1"
    ],
    "HEDVersion": "7.1.1",
    "HowToAcknowledge": "Please cite this paper: https://www.ncbi.nlm.nih.gov/pubmed/001012092119281",
    "License": "CC0",
    "Name": "The mother of all experiments",
    "ReferencesAndLinks": [
        "Alzheimer A., & Kraepelin, E. (2015). Neural correlates of presenile dementia in humans. Journal of Neuroscientific Data, 2, 234001. doi:1920.8/jndata.2015.7",
        "https://www.ncbi.nlm.nih.gov/pubmed/001012092119281"
    ],
    "description": [
        {
            "extension": ".md",
            "text": "A very detailed description с юникодом"
        }
    ],
    "entities": {
        "datatype": [
            "func"
        ],
        "extension": [
            ".json",
            ".md",
            ".nii.gz",
            ".tsv"
        ],
        "subject": [
            "01",
            "03"
        ],
        "suffix": [
            "README",
            "bold",
            "description",
            "participants"
        ],
        "task": [
            "other",
            "some"
        ]
    },
    "variables": {
        "dataset": [
            "age",
            "gender",
            "handedness",
            "hearing_problems_current",
            "language",
            "subject",
            "suffix"
        ]
    }
}"""

@known_failure_windows
@with_tree(tree=bids_template)
def test_get_metadata(path=None):
    ds = Dataset(path).create(force=True)
    meta = BIDSmeta(ds).get_metadata()
    del meta['@context']
    sort_lists_in_dict(meta)
    dump = json.dumps(meta, sort_keys=True, indent=4, ensure_ascii=False)
    assert_equal(
        dump,
        correct_metadata
    )

def sort_lists_in_dict(data_dict):
    for key, value in data_dict.items():
        if isinstance(value, list):
            data_dict[key].sort()
        if isinstance(value, dict):
            sort_lists_in_dict(data_dict[key])
