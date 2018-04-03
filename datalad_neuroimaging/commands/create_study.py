from datalad.interface.base import build_doc, Interface
from datalad.distribution.create import Create


@build_doc
class CreateStudy(Create):
    "TODO"

    from datalad.distribution.dataset import datasetmethod
    from datalad.interface.utils import eval_results

    # Note: _params_ inherited from create!

    @staticmethod
    @datasetmethod(name='create_study_raw')
    @eval_results
    def __call__(
            path=None,
            force=False,
            description=None,
            dataset=None,
            no_annex=False,
            save=True,
            annex_version=None,
            annex_backend='MD5E',
            native_metadata_type=None,
            shared_access=None,
            git_opts=None,
            annex_opts=None,
            annex_init_opts=None,
            text_no_annex=False  # changed
    ):
        from datalad.support.constraints import EnsureKeyChoice
        from datalad.distribution.dataset import Dataset
        from datalad.distribution.install import Install
        from datalad.distribution.siblings import Siblings

        import os

        for r in Create.__call__(
                path, force, description,
                dataset, no_annex, save,
                annex_version,
                annex_backend,
                native_metadata_type,
                shared_access, git_opts,
                annex_opts, annex_init_opts,
                text_no_annex,

                # Don't implicitly depend on Create's defaults, but make them
                # explicit instead:
                result_xfm=None,
                return_type='generator',
                result_filter=EnsureKeyChoice('action', ('create',)) & \
                            EnsureKeyChoice('status', ('ok', 'notneeded'))):
            yield r

            if r['type'] == 'dataset':
                study_ds = Dataset(r['path'])

                # TODO: get the actual container we are currently in
                #       - requires to get info from outside (via ENV may be)
                #       - but: we do we want to link to the _local_ container?
                #       - may be always add psydata and/or github as a remote
                # datalad run: option + config to use a paricular container
                #              => set env to propagate container's dataset into
                #                 the container itself
                #              => SINGULARITYENV_ prefix
                #
                # datalad run "command" itself needs to set the env and call:
                # THAT_ENV singularity exec configured/container  "command"

                # TODO: Issue: If we clone from psydata, we get a message from
                # datalad-install reading "access to dataset sibling
                # "psydata-store" not auto-enabled, enable with:
                # datalad siblings -d "/tmp/test/.datalad/environments/import-container"
                # enable -s psydata-store
                #
                # => It's actually enabled. Issue comes from distribution/utils:_handle_possible_annex_dataset,
                #    which looks whether that special remote is reported by name.
                #    But it isn't, since it's also 'origin'. We would need to look for annexuuid instead.

                # Note: This is a pointer to the container we are in, if it was
                # passed by the caller (which could be datalad-run) via
                # SINGULARITYENV_DATALAD_CONTAINER:

                add_sibling_dicts = [{
                    'action': 'add',
                    'name': 'github-psyinf',
                    'url': 'https://github.com/psychoinformatics-de/cbbs-imaging-container-import.git',
                }]

                # REMOVE
                add_sibling_dicts = []

                container_ds = os.environ.get('DATALAD_CONTAINER')
                if container_ds:
                    add_sibling_dicts += {
                        'action': 'add',
                        'name': 'psydata',
                        'url': "http://psydata.ovgu.de/cbbs-imaging/conv-container/.git",
                        'pushurl': ''
                    }
                else:
                    container_ds = "https://github.com/psychoinformatics-de/cbbs-imaging-container-import.git" #http://psydata.ovgu.de/cbbs-imaging/conv-container/.git"

                    # REMOVE!
                    add_sibling_dicts.append({
                        'action': 'add',
                        'name': 'psydata',
                        'url': "http://psydata.ovgu.de/cbbs-imaging/conv-container/.git",
                        'pushurl': ''
                    })

                for r_inst in study_ds.install(
                        path=".datalad/environments/import-container",
                        source=container_ds,
                        # TODO: result config
                        result_xfm=None,
                        return_type='generator',
                        result_filter=EnsureKeyChoice('action', ('install',)) & \
                                    EnsureKeyChoice('status', ('ok', 'notneeded'))
                        ):
                    yield r_inst
                    subds = Dataset(r_inst['path'])

                for sib in add_sibling_dicts:
                    # TODO: result config
                    subds.siblings(**sib)

                yield {
                    'status': 'ok',
                    'action': 'create study raw dataset',
                    'path': study_ds.path,
                    'type': 'dataset',
                    'message': None
                }


__datalad_plugin__ = CreateStudy
