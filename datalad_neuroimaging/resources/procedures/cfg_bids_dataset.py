"""Procedure to apply a sensible BIDS default setup to a dataset
"""

import sys
from datalad.distribution.dataset import require_dataset
from datalad.core.local.save import Save
from datalad.interface.run_procedure import RunProcedure

ds = require_dataset(
    sys.argv[1],
    check_installed=True,
    purpose='BIDS dataset configuration')

# unless taken care of by the template already, each item in here
# will get its own .gitattributes entry to keep it out of the annex
# give relative path to dataset root (use platform notation)
force_in_git = [
    'README',
    'CHANGES',
    'dataset_description.json',
    '.bidsignore',
]
# make an attempt to discover the prospective change in .gitattributes
# to decide what needs to be done, and make this procedure idempotent
# (for simple cases)
attr_fpath = ds.pathobj / '.gitattributes'
attrs = attr_fpath.read_text() if attr_fpath.exists() else ''
# amend gitattributes, if needed
ds.repo.set_gitattributes([
    (path, {'annex.largefiles': 'nothing'})
    for path in force_in_git
    if '{} annex.largefiles=nothing'.format(path) not in attrs
])

# leave clean
Save()(
    dataset=ds,
    path=['.gitattributes'],
    message="Apply default BIDS dataset setup",
    to_git=True,
)

# run metadata type config last, will do another another commit
RunProcedure()(
    dataset=ds,
    spec=['cfg_metadatatypes', 'bids', 'nifti1'],
)
