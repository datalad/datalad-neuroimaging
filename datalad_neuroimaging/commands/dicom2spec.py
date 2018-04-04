#!/usr/bin/python
#
# this script derives a studyspec draft from dataset's dicom metadata
#
# Note: ATM to be called from within the subdataset containing the dicoms,
# although it will store the studyspec one level up.

from datalad.support import json_py
from os.path import join as opj, exists, pardir

from datalad.interface.base import build_doc, Interface
from datalad.support.constraints import EnsureStr
from datalad.support.constraints import EnsureNone
from datalad.support.param import Parameter
from datalad.distribution.dataset import datasetmethod, EnsureDataset, \
    require_dataset
from datalad.interface.utils import eval_results

import logging
lgr = logging.getLogger('datalad.neuroimaging.dicom2spec')


def series_is_valid(series):
    # filter "Series" entries from dataset metadata here, in order to get rid of
    # things, that aren't relevant image series
    # TODO: RF: Move to rules definition

    # Note:
    # In 3T_visloc, SeriesNumber 0 is associated with ProtocolNames
    # 'DEFAULT PRESENTATION STATE' and 'ExamCard'.
    # All other SeriesNumbers have 1:1 relation to ProtocolNames and have 3-4
    # digits.
    # In 7T_ad there is no SeriesNumber 0 and the SeriesNumber doesn't have a 1:1
    # relation to ProtocolNames
    # Note: There also is a SeriesNumber 99 with protocol name 'Phoenix Document'?

    # Philips 3T Achieva
    if series['SeriesNumber'] == 0 and \
                    series['ProtocolName'] in ['DEFAULT PRESENTATION STATE',
                                               'ExamCard']:
        return False
    return True


@build_doc
class Dicom2Spec(Interface):
    """TODO
    """

    _params_ = dict(

            # TODO: dataset may be should be the dicom subds if given

            dataset=Parameter(
                    args=("-d", "--dataset"),
                    metavar='PATH',
                    doc="""specify the study dataset.  If
            no dataset is given, an attempt is made to identify the dataset
            based on the current working directory and/or the `path` given""",
                    constraints=EnsureDataset() | EnsureNone()),
            source=Parameter(
                    args=("source",),
                    metavar='SOURCE',
                    doc="""path of the dicom archive to be imported.""",
                    constraints=EnsureStr() | EnsureNone()),
            spec=Parameter(
                    args=("spec",),
                    metavar="SPEC",
                    doc="""session identifier for the imported DICOM files. If not 
            specified, an attempt will be made to derive SESSION from DICOM 
            headers.""",
                    constraints=EnsureStr() | EnsureNone()),
    )

    @staticmethod
    @datasetmethod(name='ni_dicom2spec')
    @eval_results
    def __call__(source=None, spec=None, dataset=None):

        if not source:
            dicom_ds = require_dataset(dataset, check_installed=True,
                                       purpose="dicom2spec")
        if source and not dataset:
            dicom_ds = require_dataset(source, check_installed=True,
                                       purpose="dicom2spec")

        if source and dataset:
            # TODO: Don't know yet
            raise ValueError

        # TODO: Naming. It's actually not a study specification but only a
        # "session" or "acquisition" or "scan" specification.
        spec_file = opj(dicom_ds.path, pardir, 'studyspec.json') if not spec \
            else spec

        # TODO: Proper result yielding. Particularly errors!
        ##################################################################

        # get a dataset level metadata:
        ds_metadata = dicom_ds.metadata(reporton='datasets')[0]

        if 'dicom' not in ds_metadata['metadata']:
            lgr.error("Found no DICOM metadata in %s", dicom_ds)
            exit(1)

        if 'Series' not in ds_metadata['metadata']['dicom'] or \
                not ds_metadata['metadata']['dicom']['Series']:
            lgr.error("No image series detected in DICOM metadata of %s",
                      dicom_ds)
            exit(1)

        spec_series_list = json_py.load(spec_file) if exists(spec_file) \
            else list()
        #protocol_counter = dict()

        lgr.debug("Discovered %s image series.",
                  len(ds_metadata['metadata']['dicom']['Series']))

        # generate a list of dicts, with the "rule-proof" entries:
        base_list = []
        for series in ds_metadata['metadata']['dicom']['Series']:
            base_list.append({
                # Note: The first 4 entries aren't a dict and have no
                # "approved flag", since they are automatically managed
                'type': 'dicomseries',
                'status': None,  # TODO: process state convention; flags
                'location': dicom_ds.path,
                'uid': series['SeriesInstanceUID'],
                'converter': {
                    'value': 'heudiconv' if series_is_valid(series) else 'ignore',
                    # TODO: not clear yet, what exactly to specify here
                    'approved': False},
            })

        # get rules to apply:
        from dicom2bids_rules import get_rules_from_metadata  # TODO: RF?
        rules = get_rules_from_metadata(
                ds_metadata['metadata']['dicom']['Series'])
        for rule_cls in rules:
            rule = rule_cls(ds_metadata['metadata']['dicom']['Series'])
            for idx, values in zip(range(len(base_list)), rule()):
                for k in values.keys():
                    base_list[idx][k] = {'value': values[k],
                                         'approved': False}

        # merge with existing spec:
        for series in base_list:
            existing = [i for s, i in
                        zip(spec_series_list, range(len(spec_series_list)))
                        if s['uid'] == series['uid']]
            if existing:
                lgr.debug("Updating existing spec for image series %s",
                          series['uid'])
                # we already had data of that series in the spec;
                spec_series_list[existing[0]].update(series)
            else:
                lgr.debug("Creating spec for image series %s", series['uid'])
                spec_series_list.append(series)

        # TODO: unify
        import json
        json.dump(spec_series_list, open(spec_file, 'w'), indent=4)
        from datalad.distribution.add import Add

        Add.__call__(spec_file, save=True,
                     message="[DATALAD-NI] Added study specification snippet "
                             "for %s" % dicom_ds.path)


# TODO: Apply bids rules for naming (heuristic also!)
# checkout python bids-validator, which might provide them




