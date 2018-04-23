from os.path import dirname, normpath, join as opj, pardir

from datalad.api import Dataset
from datalad.coreapi import install
from datalad.tests.utils import ok_clean_git

import datalad_neuroimaging
_modpath = dirname(datalad_neuroimaging.__file__)


def get_dicom_dataset(flavor):
    ds = install(
        dataset=normpath(opj(_modpath, pardir)),
        path=opj(_modpath, 'tests', 'data', 'dicoms', flavor))
    # fail on any "surprising" changes made to this dataset
    ok_clean_git(ds.path)
    return ds


def get_bids_dataset():
    bids_ds = Dataset(path=opj(_modpath, 'tests', 'data', 'bids'))
    if bids_ds.is_installed():
        return bids_ds
    # make one
    dicom_ds = get_dicom_dataset('structural')
    bids_ds.create()
    # place dicoms in the mandated shadow tree
    dicom_ds = bids_ds.install(
        source=dicom_ds,
        path=opj('sourcedata', 'sub-02', 'ses-structural'),
        reckless=True)
    # dicom dataset is preconfigured for metadata extraction
    bids_ds.aggregate_metadata(recursive=True)
    ok_clean_git(dicom_ds.path)
    # pull subject ID from metadata
    res = bids_ds.metadata(
        dicom_ds.path, reporton='datasets', return_type='item-or-list',
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
    # conversion to BIDS
    from mock import patch
    import heudiconv.cli.run
    heudiconv.cli.run.main([
        '-f', 'reproin',
        # TODO fix DICOMs to not have a 'sub' prefix
        '-s', subj_id[3:],
        '-c' 'dcm2niix',
        '-b',
        '-o', bids_ds.path,
        '-l', '',
        '--files', opj(dicom_ds.path, 'dicoms'),
    ])
    # cleanup: with heudiconv -b we can dicom tarballs per sequence
    # while this is nice, we already have a subdataset with dicoms
    # and don't need two, and in the general case people will
    # rarely by able to share these, and they require additional
    # storage
    # XXX kill them for now
    # TODO heudoconv should have a switch to prevent this tarball
    # generation
    import shutil
    import os
    shutil.rmtree(opj(
        bids_ds.path, 'sourcedata', 'sub-02', 'anat'))
    os.remove(opj(
        bids_ds.path, 'sourcedata', 'README'))
    # TODO decide on the fate of .heudiconv/
    shutil.rmtree(opj(
        bids_ds.path, '.heudiconv'))
    # and commit the rest
    bids_ds.add('.', message="Add BIDS-converted content")
    bids_ds.config.add('datalad.metadata.nativetype', 'bids',
                       where='dataset', reload=False)
    bids_ds.config.add('datalad.metadata.nativetype', 'nifti1',
                       where='dataset', reload=True)
    bids_ds.save(message='Metadata type config')
    # loose dicom dataset
    bids_ds.uninstall(dicom_ds.path, check=False)
    # no need for recursion, we already have the dicom dataset's
    # stuff on record
    bids_ds.aggregate_metadata(recursive=False, incremental=True)
    ok_clean_git(bids_ds.path)


def create_dicom_tarball(flavor, path):
    import tarfile
    ds = get_dicom_dataset(flavor=flavor)
    with tarfile.open(path, "w:gz") as tar:
        tar.add(ds.path)
    return path
