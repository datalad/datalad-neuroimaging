from os.path import join as opj

import datalad_neuroimaging
from datalad.api import Dataset
from datalad.api import ni_create_study

from datalad.tests.utils import assert_result_count
from datalad.tests.utils import ok_clean_git
from datalad.tests.utils import with_tempfile

from datalad_neuroimaging.tests.utils import get_dicom_dataset, create_dicom_tarball


@with_tempfile
@with_tempfile
def test_import_tarball(filename, ds_path):

    create_dicom_tarball('structural', filename)
    ds = ni_create_study(ds_path)
    ds.ni_import_dicomtarball(path=filename, session='acq100')

