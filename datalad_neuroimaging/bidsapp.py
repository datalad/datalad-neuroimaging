import logging
from os.path import join as opj
from datalad.interface.base import build_doc, Interface
from datalad.support.param import Parameter
from datalad.distribution.dataset import datasetmethod, EnsureDataset, \
    require_dataset, resolve_path, Dataset
from datalad.interface.utils import eval_results
from datalad.support.constraints import EnsureStr
from datalad.support.constraints import EnsureNone
from datalad.support.exceptions import InsufficientArgumentsError
from datalad.coreapi import run
from datalad.interface.results import get_status_dict


lgr = logging.getLogger("datalad.cbbsimaging.bidsapp")


@build_doc
class BidsApp(Interface):
    """Run a BIDSApp on the dataset
    """

    _params_ = dict(
        dataset=Parameter(
            args=("-d", "--dataset"),
            doc="""dataset to run the BIDSApp on""",
            constraints=EnsureDataset() | EnsureNone()),
        cmd=Parameter(
            args=("cmd",),
            doc="""Preconfigured BIDSApp to run. The name corresponds to
            datalad.neuroimaging.bidsapp.NAME configuration.""",
            metavar="CMD",
            constraints=EnsureStr() | EnsureNone())
        )

    @staticmethod
    @datasetmethod(name='run_bidsapp')
    @eval_results
    def __call__(cmd, dataset=None):

        dataset = require_dataset(dataset, check_installed=True,
                                  purpose="run BIDS App")

        container_name = \
            dataset.config.get("datalad.neuroimaging.bidsapp.%s.container-name"
                               % cmd)
        if not container_name:
            raise ValueError("Missing configuration for "
                             "datalad.neuroimaging.bidsapp.%s.container-name"
                             % cmd)

        container_ds = Dataset(opj(dataset.path, ".git",
                                   "environment", container_name))
        if not container_ds.is_installed():
            source = \
                dataset.config.get("datalad.neuroimaging.bidsapp.%s.container-url"
                                   % cmd)
            if not source:
                raise ValueError("Missing configuration for "
                                 "datalad.neuroimaging.bidsapp.%s.container-url"
                                 % cmd)

            lgr.info("Installing BIDSApp %s from %s", container_name, source)
            for r in dataset.install(path=container_ds.path, source=source,
                                     get_data=True):

                if r['type'] == 'dataset':
                    container_ds = Dataset(r['path'])
                yield r

        image_name = \
            container_ds.config.get("datalad.neuroimaging.bidsapp.container")
        if image_name is None:
            image_name = ""
        else:
            if not container_ds.repo.file_has_content(image_name):
                container_ds.get(image_name)

        image_exec = \
            container_ds.config.get("datalad.neuroimaging.bidsapp.exec")
        if not image_exec:
            raise ValueError("Missing configuration for "
                             "datalad.neuroimaging.bidsapp.exec in %s" %
                             container_ds.path)

        cmd_call = \
            dataset.config.get("datalad.neuroimaging.bidsapp.%s.call" % cmd)
        if not cmd_call:
            raise ValueError("Missing configuration for "
                             "datalad.neuroimaging.bidsapp.%s.call" % cmd)

        run_cmd = "{exec_} {img} {call}".format(exec_=image_exec,
                                                img="" if image_name is None
                                                else opj(container_ds.path,
                                                         image_name),
                                                call=cmd_call)

        for r in dataset.run(run_cmd, message="Run of bidsapp %s" % cmd):
            yield r
