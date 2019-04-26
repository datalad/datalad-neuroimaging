"""Procedure to apply a sensible BIDS default setup to a dataset
"""

import sys
import os.path as op
from datalad.distribution.dataset import require_dataset

# bound dataset methods
import datalad.distribution.add
import datalad.interface.run_procedure

ds = require_dataset(
    sys.argv[1],
    check_installed=True,
    purpose='BIDS dataset setup')

# TODO: This looks like it was supposed to be a default README but isn't used
# ATM.
README_code = """\
All custom code goes into the directory. All scripts should be written such
that they can be executed from the root of the dataset, and are only using
relative paths for portability.
"""

# unless taken care of by the template already, each item in here
# will get its own .gitattributes entry to keep it out of the annex
# give relative path to dataset root (use platform notation)
force_in_git = [
    'README',
    'CHANGES',
    'dataset_description.json',
]

###################################################################
to_add = set()

# configure minimal set of metadata extractors
ds.run_procedure(['cfg_metadatatypes', 'bids', 'nifti1'])

# amend gitattributes
ds.repo.set_gitattributes([(path, {'annex.largefiles': 'nothing'})
                           for path in force_in_git])

# leave clean
ds.add('.gitattributes', message="[HIRNI] Default BIDS dataset setup")
