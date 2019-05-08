from datalad.tests.utils import (
    with_tempfile,
    eq_,
    ok_clean_git,
)
from datalad.distribution.dataset import Dataset
import datalad.interface.run_procedure


@with_tempfile
def test_bids_procedure(path):
    ds = Dataset(path).create()
    ds.run_procedure(['cfg_bids'])
    ds.config.reload()
    eq_('nothing',
        ds.repo.get_gitattributes(
            '.bidsignore')['.bidsignore']['annex.largefiles'])
    eq_(set(('bids', 'nifti1')),
        set(ds.config['datalad.metadata.nativetype']))
    # check that it does nothing on a second run
    origsha = ds.repo.get_hexsha()
    ds.run_procedure(['cfg_bids'])
    eq_(origsha, ds.repo.get_hexsha())
    ok_clean_git(ds.path)

