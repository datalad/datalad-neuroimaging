from os.path import dirname, normpath, join as opj, pardir
import os.path as op

from datalad.api import Dataset
from datalad.api import export_archive
from datalad.coreapi import install
from datalad.tests.utils import ok_clean_git
from datalad.tests.utils import SkipTest
from datalad.interface.common_cfg import dirs as appdirs

import datalad_neuroimaging


def get_sourcerepo():
    srcrepopath = normpath(
        opj(dirname(datalad_neuroimaging.__file__), pardir))
    srcrepo = Dataset(srcrepopath)
    if not srcrepo.is_installed():
        srcrepo = install(
            source='https://github.com/datalad/datalad-neuroimaging.git',
            path=opj(appdirs.user_cache_dir, 'datalad_neuroimaging_srcrepo'))
        # this will eventually show us if we can properly upgrade submodules
        srcrepo.update(merge=True)
        # TODO we might want to try to check out a tag that corresponds to the
        # installed version
    return srcrepo


def get_dicom_dataset(flavor):
    srcrepo = get_sourcerepo()
    ds = install(
        dataset=srcrepo,
        path=opj(srcrepo.path, 'datalad_neuroimaging', 'tests', 'data',
                 'dicoms', flavor))
    # fail on any "surprising" changes made to this dataset
    ok_clean_git(ds.path)
    return ds


def get_bids_dataset():
    srcrepo = get_sourcerepo()
    bids_ds = Dataset(path=opj(
        srcrepo.path, 'datalad_neuroimaging', 'tests', 'data', 'bids'))
    if bids_ds.is_installed():
        return bids_ds
    try:
        import heudiconv
    except ImportError:
        raise SkipTest
    # make one
    bids_ds.create()
    # place dicoms in the mandated shadow tree
    structdicom_ds = bids_ds.install(
        source=get_dicom_dataset('structural'),
        path=opj('sourcedata', 'sub-02', 'ses-structural'),
        reckless=True)
    funcdicom_ds = bids_ds.install(
        source=get_dicom_dataset('functional'),
        path=opj('sourcedata', 'sub-02', 'ses-functional'),
        reckless=True)
    # dicom dataset is preconfigured for metadata extraction
    # XXX this is the slowest step of the entire procedure
    # reading 5k dicoms of the functional data
    bids_ds.aggregate_metadata(recursive=True)
    # pull subject ID from metadata
    res = bids_ds.metadata(
        funcdicom_ds.path, reporton='datasets', return_type='item-or-list',
        result_renderer='disabled')
    subj_id = res['metadata']['dicom']['Series'][0]['PatientID']
    # prepare for incoming BIDS metadata that we will want to keep in
    # Git -- templates would be awesome!
    with open(opj(bids_ds.path, '.gitattributes'), 'a') as ga:
        # except for hand-picked global metadata, we want anything
        # to go into the annex to be able to retract files after
        # publication
        ga.write('** annex.largefiles=anything\n')
        for fn in ('CHANGES', 'README', 'dataset_description.json'):
            # but not these
            ga.write('{} annex.largefiles=nothing\n'.format(fn))
    bids_ds.add('.gitattributes', to_git=True,
                message='Initial annex entry configuration')
    ok_clean_git(bids_ds.path)
    # conversion of two DICOM datasets to one BIDS dataset
    for label, ds, scanlabel in (
            # structural needs to come first or else heudiconv
            # will try to rewrite the events.tsv for the functional
            # run, for some strange reason
            ('structural', structdicom_ds, 'anat'),
            ('functional', funcdicom_ds, 'func')):
        bids_ds.run([
            'heudiconv',
            '-f', 'reproin',
            # TODO fix DICOMs to not have a 'sub' prefix
            '-s', subj_id,
            '-c', 'dcm2niix',
            # TODO decide on the fate of .heudiconv/
            # but ATM we need to (re)move it:
            # https://github.com/nipy/heudiconv/issues/196
            '-o', opj(bids_ds.path, '.git', 'stupid', label),
            '-b',
            '-a', bids_ds.path,
            '-l', '',
            # avoid gory details provided by dcmstack, we have them in
            # the aggregated DICOM metadata already
            '--minmeta',
            '--files', opj(ds.path, 'dicoms')],
            message="DICOM conversion of {} scans".format(label))
        # remove unwanted stuff that cannot be disabled ATM
        # https://github.com/nipy/heudiconv/issues/195
        # TODO should be removed eventually
        bids_ds.remove(
            [p for p in (opj('sourcedata', 'sub-02', scanlabel),
                         opj('sourcedata', 'README'))
             if op.lexists(opj(bids_ds.path, p))],
            check=False)

    bids_ds.config.add('datalad.metadata.nativetype', 'bids',
                       where='dataset', reload=False)
    bids_ds.config.add('datalad.metadata.nativetype', 'nifti1',
                       where='dataset', reload=True)
    # XXX need to `add` specifically to make it work in direct mode
    #bids_ds.save(message='Metadata type config')
    bids_ds.add('.', message='Metadata type config')
    # loose dicom datasets
    bids_ds.uninstall(
        [structdicom_ds.path, funcdicom_ds.path],
        check=False)
    # no need for recursion, we already have the dicom dataset's
    # stuff on record
    bids_ds.aggregate_metadata(recursive=False, incremental=True)
    ok_clean_git(bids_ds.path)
    return bids_ds


def create_dicom_tarball(flavor, path):

    ds = get_dicom_dataset(flavor=flavor)
    ds.export_archive(path, archivetype="tar", compression="gz",
                      missing_content="ignore")
    return path
