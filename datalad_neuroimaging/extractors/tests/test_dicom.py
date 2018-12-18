# emacs: -*- mode: python-mode; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Test DICOM extractor"""

from datalad.tests.utils import SkipTest
try:
    from datalad_neuroimaging.extractors.dicom import MetadataExtractor as DicomExtractor
except ImportError:
    raise SkipTest

from shutil import copy
import os.path as op
from datalad.api import Dataset
from datalad.tests.utils import with_tempfile
from datalad.tests.utils import ok_clean_git
from datalad.tests.utils import assert_status
from datalad.tests.utils import assert_result_count
from datalad.tests.utils import eq_
from datalad.tests.utils import assert_dict_equal
from datalad.tests.utils import assert_in
from datalad.tests.utils import assert_not_in
from . import datalad_extracts_annex_key

@with_tempfile(mkdir=True)
def test_dicom(path):
    ds = Dataset(path).create()
    ds.config.add('datalad.metadata.nativetype', 'dicom', where='dataset')
    copy(
        op.join(op.dirname(op.dirname(op.dirname(__file__))), 'tests', 'data', 'files', 'dicom.dcm'),
        path)
    ds.add('.')
    ok_clean_git(ds.path)
    res = ds.aggregate_metadata()
    assert_status('ok', res)
    # query for the file metadata
    res = ds.metadata('dicom.dcm')
    assert_result_count(res, 1)
    # from this extractor
    meta = res[0]['metadata']['dicom']
    assert_in('@context', meta)
    # no point in testing ALL keys, but we got plenty
    assert(len(meta.keys()) > 70)
    eq_(meta['SeriesDate'], '20070205')
    # Actually a tricky one of the dcm.multival.MultiValue type
    # which we should extract as a list
    # https://github.com/datalad/datalad-neuroimaging/issues/49
    eq_(meta['ImageType'], ['ORIGINAL', 'PRIMARY', 'EPI', 'NONE'])
    # make sure we have PatientName -- this is not using a basic data type, but
    # dicom.valuerep.PersonName3 -- conversion should have handled that
    # we can only test if the key is there, the source dicom has an empty
    # string as value
    eq_(meta['PatientName'], '')

    # now ask for the dataset metadata, which should have both the unique props
    # and a list of imageseries (one in this case, but a list)
    res = ds.metadata(reporton='datasets')
    assert_result_count(res, 1)
    dsmeta = res[0]['metadata']['dicom']
    # same context
    assert_dict_equal(meta['@context'], dsmeta['@context'])
    meta.pop('@context')
    seriesmeta = dsmeta['Series']
    eq_(seriesmeta[0].pop('SeriesDirectory'), op.curdir)
    eq_(dsmeta['Series'], [meta])

    # for this artificial case pretty much the same info also comes out as
    # unique props, but wrapped in lists
    ucp = res[0]['metadata']["datalad_unique_content_properties"]['dicom']
    assert_dict_equal(
        {k: [v]
         for k, v in dsmeta['Series'][0].items()
         if k not in DicomExtractor._unique_exclude and k in ucp},
        {k: v
         for k, v in ucp.items()
         if k not in DicomExtractor._unique_exclude})

    # buuuut, if we switch of file-based metadata storage
    ds.config.add('datalad.metadata.aggregate-content-dicom', 'false', where='dataset')
    ds.aggregate_metadata()
    res = ds.metadata(reporton='datasets')

    if not datalad_extracts_annex_key:
        # the auto-uniquified bits are gone but the Series description stays
        assert_not_in("datalad_unique_content_properties", res[0]['metadata'])
    eq_(dsmeta['Series'], [meta])
