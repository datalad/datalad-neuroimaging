import datalad.interface.run_procedure
from datalad.distribution.dataset import Dataset
from datalad.tests.utils_pytest import (
    eq_,
    known_failure_osx,
    known_failure_windows,
    ok_clean_git,
    with_tempfile,
)


@known_failure_windows
@known_failure_osx
@with_tempfile
def test_bids_procedure(path=None):
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
