from six import reraise
from os import makedirs
from os.path import join as opj
from datalad.consts import ARCHIVES_SPECIAL_REMOTE, DATALAD_SPECIAL_REMOTES_UUIDS
from datalad.interface.base import build_doc, Interface
from datalad.support.constraints import EnsureStr
from datalad.support.constraints import EnsureNone
from datalad.support.constraints import EnsureKeyChoice
from datalad.support.param import Parameter
from datalad.distribution.dataset import datasetmethod, EnsureDataset, \
    require_dataset
from datalad.interface.utils import eval_results
from datalad.distribution.create import Create
from datalad.dochelpers import exc_str
from datalad.support.network import get_local_file_url

import logging
lgr = logging.getLogger('datalad.neuroimaging.import_dicoms')


def _import_dicom_tarball(target_ds, tarball, filename):

    # # TODO: doesn't work for updates yet:
    # # - branches are expected to not exist yet
    target_ds.repo.checkout('incoming', options=['-b'])
    target_ds.repo.init_remote(ARCHIVES_SPECIAL_REMOTE,
                            options=['encryption=none', 'type=external',
                                     'externaltype=%s' % ARCHIVES_SPECIAL_REMOTE,
                                     'autoenable=true',
                                     'uuid=%s' % DATALAD_SPECIAL_REMOTES_UUIDS[ARCHIVES_SPECIAL_REMOTE]
                                     ]
                          )

    target_ds.repo.add_url_to_file(file_=filename, url=get_local_file_url(tarball))
    target_ds.repo.commit(msg="Retrieved %s" % tarball)
    target_ds.repo.checkout('incoming-processed', options=['--orphan'])
    if target_ds.repo.dirty:
        target_ds.repo.remove('.', r=True, f=True)

    target_ds.repo.merge('incoming', options=["-s", "ours", "--no-commit"],
                         expect_stderr=True)
    target_ds.repo._git_custom_command([], "git read-tree -m -u incoming")

    from datalad.coreapi import add_archive_content
    # # TODO: Reconsider value of --existing
    add_archive_content(archive=filename,
                        annex=target_ds.repo,
                        existing='archive-suffix',
                        delete=True,
                        commit=False,
                        allow_dirty=True)

    target_ds.repo.commit(msg="Extracted %s" % tarball)
    target_ds.repo.checkout('master')
    target_ds.repo.merge('incoming-processed', options=["--allow-unrelated"])


def _create_subds_from_tarball(tarball, targetdir):

    from os.path import basename
    filename =basename(tarball)

    importds = Create.__call__(opj(targetdir, "dicoms"),
                               native_metadata_type='dicom',
                               return_type='item-or-list',
                               result_xfm='datasets',
                               result_filter=
                               EnsureKeyChoice('action', ('create',)) &
                               EnsureKeyChoice('status', ('ok', 'notneeded'))
                               )

    _import_dicom_tarball(importds, tarball, filename)

    importds.config.add(var="datalad.metadata.aggregate-content-dicom",
                        value='false', where="dataset")
    # TODO: file an issue: config.add can't convert False to 'false' on its own
    # (But vice versa while reading IIRC)
    importds.config.add(var="datalad.metadata.maxfieldsize", value='10000000',
                        where="dataset")
    importds.add(opj(".datalad", "config"), save=True,
                 message="[DATALAD] initial config for DICOM metadata")
    importds.aggregate_metadata()
    importds.install(path=opj(".datalad", "environments", "import-container"),
                     source="http://psydata.ovgu.de/cbbs-imaging/conv-container/.git")

    return importds


def _guess_session_and_move(ds, target_ds):
    from datalad.coreapi import metadata

    res = ds.metadata(reporton='datasets', return_type='item-or-list',
                      result_renderer='disabled')
    # there should be exactly one result and therefore a dict
    assert isinstance(res, dict)
    # TODO: This should be part of the rule set
    ses = res['metadata']['dicom']['Series'][0]['PatientID']

    from os import rename
    rename(opj(target_ds.path, 'datalad_ni_import'), opj(target_ds.path, ses))

#    from datalad.utils import rmtree
#    rmtree(ses_dir)

    from datalad.coreapi import Dataset
    return Dataset(opj(target_ds.path, ses, 'dicoms'))


@build_doc
class ImportDicoms(Interface):
    """Import a DICOM archive into a study raw dataset.

    This creates a subdataset with the DICOM files under SESSION/dicoms.
    Furthermore a study specification will automatically be prefilled, based on
    the metadata in DICOM headers."""

    _params_ = dict(
        dataset=Parameter(
            args=("-d", "--dataset"),
            metavar='PATH',
            doc="""specify the dataset to import the DICOM archive into.  If
            no dataset is given, an attempt is made to identify the dataset
            based on the current working directory and/or the `path` given""",
            constraints=EnsureDataset() | EnsureNone()),
        path=Parameter(
            args=("path",),
            metavar='PATH',
            doc="""path of the dicom archive to be imported.""",
            constraints=EnsureStr()),
        session=Parameter(
            args=("session",),
            metavar="SESSION",
            doc="""session identifier for the imported DICOM files. If not 
            specified, an attempt will be made to derive SESSION from DICOM 
            headers.""",
            nargs="?",
            constraints=EnsureStr() | EnsureNone()),
    )

    @staticmethod
    @datasetmethod(name='ni_import_dicomtarball')
    @eval_results
    def __call__(path, session=None, dataset=None):

        ds = require_dataset(dataset, check_installed=True,
                             purpose="import DICOM session")

        if session:
            # session was specified => we know where to create subds
            ses_dir = opj(ds.path, session)
            makedirs(ses_dir, exist_ok=True)

            dicom_ds = _create_subds_from_tarball(path, ses_dir)

        else:
            # we don't know the session yet => create in tmp

            ses_dir = opj(ds.path, 'datalad_ni_import')
            from os.path import exists
            assert not exists(ses_dir)
            # TODO: don't assert; check and adapt instead

            try:
                dicom_ds = _create_subds_from_tarball(path, ses_dir)
                dicom_ds = _guess_session_and_move(dicom_ds, ds)
            except Exception as e:
                # remove tmp and reraise
                lgr.debug("Exception branch: Killing temp dataset ...")

                from datalad.utils import rmtree
                rmtree(ses_dir)
                # TODO: reraise()
                raise

        ds.add(dicom_ds.path)
        ds.aggregate_metadata(dicom_ds.path)

        from os.path import pardir

        from datalad.api import Dataset
        from datalad.api import ni_import_dicomtarball

        ds.ni_dicom2spec(path=dicom_ds.path, spec=opj(dicom_ds.path, pardir,
                                                      "studyspec.json"))

        # TODO: yield error results etc.
        yield dict(status='ok',
                   path=dicom_ds.path,
                   type='dataset',
                   action='import DICOM tarball',
                   logger=lgr)



