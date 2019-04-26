from datalad.tests.utils import (
    with_tempfile,
    eq_,
    assert_repo_status,
)
from datalad.distribution.dataset import Dataset
import datalad.interface.run_procedure


@with_tempfile
def test_bids_procedure(path):
    ds = Dataset(path).rev_create()
    ds.run_procedure(['cfg_bids_dataset'])
    ds.config.reload()
    eq_('nothing',
        ds.repo.get_gitattributes(
            '.bidsignore')['.bidsignore']['annex.largefiles'])
    eq_(set(('bids', 'nifti1')),
        set(ds.config['datalad.metadata.nativetype']))
    # check that it does nothing on a second run
    origsha = ds.repo.get_hexsha()
    ds.run_procedure(['cfg_bids_dataset'])
    eq_(origsha, ds.repo.get_hexsha())
    assert_repo_status(ds.path)

