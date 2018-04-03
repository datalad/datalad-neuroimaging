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


def _import_dicom_tarball(target_ds, tarball, filename):

    # # $1 path to tarball
    # # $2 target filename to use
    # local path="$1"
    # local filename="$2"
    #
    # # TODO: doesn't work for updates yet:
    # # - branches are expected to not exist yet
    target_ds.repo.checkout('incoming', options=['-b'])
    target_ds.init_remote(ARCHIVES_SPECIAL_REMOTE,
                            options=['encryption=none', 'type=external',
                                     'externaltype=%s' % ARCHIVES_SPECIAL_REMOTE,
                                     'autoenable=true',
                                     'uuid=%s' % DATALAD_SPECIAL_REMOTES_UUIDS[ARCHIVES_SPECIAL_REMOTE]
                                     ]
                            )

    target_ds.add_url_to_file(file_=filename, url=tarball)
    target_ds.commit(msg="Retrieved %s" % tarball)
    target_ds.checkout('incoming-processed', options=['--orphan'])
    if target_ds.repo.dirty:
        target_ds.repo.remove('.', r=True, f=True)


    # git merge incoming -s ours --no-commit
    # git read-tree -m -u incoming
    target_ds.repo.merge('incoming', options=["-s", "ours", "--no-commit"],
                         expect_stderr=True)
    target_ds.repo._git_custom_command([], "git read-tree -m -u incoming")

    # # TODO: Reconsider value of --existing
    
    target_ds.add_archive_content()
    # datalad add-archive-content --existing archive-suffix --delete --no-commit --allow-dirty "$filename"


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
                        value=False,where="dataset")
    importds.config.add(var="datalad.metadata.maxfieldsize", value=10000000,
                        where="dataset")
    importds.add(opj(".datalad", "config"), save=True,
                 message="[DATALAD] initial config for DICOM metadata")
    importds.aggregate_metadata()
    importds.install(path=opj(".datalad","environments","import-container"),
                     source="http://psydata.ovgu.de/cbbs-imaging/conv-container/.git")


def _guess_session_and_move():
    pass

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
            constraints=EnsureStr() | EnsureNone()),
    )

    @staticmethod
    @datasetmethod(name='create_study_raw')
    @eval_results
    def __call__(path, session=None, dataset=None):

        ds = require_dataset(dataset, check_installed=True,
                             purpose="import DICOM session")

        if session:
            # session was specified => we know where to create subds
            ses_dir = opj(ds.path, session)
            makedirs(ses_dir, exist_ok=True)

            _create_subds_from_tarball()

            dicom_ds =
        else:
            # we don't know the session yet => create in tmp
            from tempfile import mkdtemp
            ses_dir = mkdtemp(dir=True)

            try:
                _create_subds_from_tarball()
                _guess_session_and_move()
                # SES=$(datalad --output-format="{metadata[dicom][Series][0][PatientID]}" metadata -d "$SUB_TMP/dicoms" --reporton=datasets)
                #     # move subdataset from TMP to actual mount point
                #     mv "$SUB_TMP/" "$SES/"
                dicom_ds =
            except Exception as e:
                # remove tmp and reraise
                from datalad.utils import rmtree
                rmtree(ses_dir)
                # TODO: reraise()
                raise


        ds.add(dicom_ds.path)
        ds.aggregate_metadata(dicom_ds.path)


        # # initialize study specification
        # cd "$SES/dicoms"
        # prepare_study_spec.py
        # cd "$OLD_PWD"

        # TODO:
        # yield



