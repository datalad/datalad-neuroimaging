# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Metadata extractor for BIDS dataset-level information"""
import logging
from telnetlib import STATUS
from uuid import UUID
from bids import BIDSLayout
from pathlib import Path
from datalad_metalad.extractors.base import DataOutputCategory, ExtractorResult, DatasetMetadataExtractor
from datalad.interface.results import get_status_dict
from datalad.log import log_progress
from datalad.metadata.definitions import vocabulary_id
from datalad.utils import ensure_unicode
from typing import Dict, List, Union

lgr = logging.getLogger('datalad.metadata.extractors.bids_dataset')

# Main properties used in BIDS v1.6.0 dataset description
class BIDSProperties:
    NAME = "Name"
    BIDSVERSION = "BIDSVersion"
    DATASETTYPE = "DatasetType"
    LICENSE = "License"
    AUTHORS = "Authors"
    ACKNOWLEDGEMENTS = "Acknowledgements"
    HOWTOACKNOWLEDGE = "HowToAcknowledge"
    FUNDING = "Funding"
    ETHICSAPPROVALS = "EthicsApprovals"
    REFSANDLINKS = "ReferencesAndLinks"
    DATASETDOI = "DatasetDOI"
    HEDVERSION = "HEDVersion"
    README = "ReadMe"

# Main entities used in BIDS v1.6.0 filenames
class BIDSEntities:
    """"""
    SUBJECT = 'subject'
    SESSION = 'session'
    TASK = 'task'
    ACQUISITION = 'acquisition'
    CEAGENT = 'ceagent'
    RECONSTRUCTION = 'reconstruction'
    DIRECTION = 'direction'
    RUN = 'run'
    PROC = 'proc'
    MODALITY = 'modality'
    ECHO = 'echo'
    FLIP = 'flip'
    INV = 'inv'
    MT = 'mt'
    PART = 'part'
    RECORDING = 'recording'
    SPACE = 'space'
    SUFFIX = 'suffix'
    SCANS = 'scans'
    FMAP = 'fmap'
    DATATYPE = 'datatype'
    EXTENSION = 'extension'

BIDSCONTEXT = {
    "@id": "https://doi.org/10.5281/zenodo.4710751",
    'description': 'ad-hoc vocabulary for the Brain Imaging Data Structure (BIDS) standard v1.6.0',
    'type': vocabulary_id,
}

REQUIRED_BIDS_FILES = ['dataset_description.json', 'participants.tsv']

DATASET = 'dataset'

BIDS_PROPERTIES_MAPPING= {
    BIDSProperties.NAME: BIDSProperties.NAME,
    BIDSProperties.BIDSVERSION: BIDSProperties.BIDSVERSION,
    BIDSProperties.DATASETTYPE: BIDSProperties.DATASETTYPE,
    BIDSProperties.LICENSE: BIDSProperties.LICENSE,
    BIDSProperties.AUTHORS: BIDSProperties.AUTHORS,
    BIDSProperties.ACKNOWLEDGEMENTS: BIDSProperties.ACKNOWLEDGEMENTS,
    BIDSProperties.HOWTOACKNOWLEDGE: BIDSProperties.HOWTOACKNOWLEDGE,
    BIDSProperties.FUNDING: BIDSProperties.FUNDING,
    BIDSProperties.ETHICSAPPROVALS: BIDSProperties.ETHICSAPPROVALS,
    BIDSProperties.REFSANDLINKS: BIDSProperties.REFSANDLINKS,
    BIDSProperties.DATASETDOI: BIDSProperties.DATASETDOI,
    BIDSProperties.HEDVERSION: BIDSProperties.HEDVERSION,
}

BIDS_ENTITIES_MAPPING = {
    BIDSEntities.SUBJECT: BIDSEntities.SUBJECT,
    BIDSEntities.SESSION: BIDSEntities.SESSION,
    BIDSEntities.TASK: BIDSEntities.TASK,
    BIDSEntities.ACQUISITION: BIDSEntities.ACQUISITION,
    BIDSEntities.CEAGENT: BIDSEntities.CEAGENT,
    BIDSEntities.RECONSTRUCTION: BIDSEntities.RECONSTRUCTION,
    BIDSEntities.DIRECTION: BIDSEntities.DIRECTION,
    BIDSEntities.RUN: BIDSEntities.RUN,
    BIDSEntities.PROC: BIDSEntities.PROC,
    BIDSEntities.MODALITY: BIDSEntities.MODALITY,
    BIDSEntities.ECHO: BIDSEntities.ECHO,
    BIDSEntities.FLIP: BIDSEntities.FLIP,
    BIDSEntities.INV: BIDSEntities.INV,
    BIDSEntities.MT: BIDSEntities.MT,
    BIDSEntities.PART: BIDSEntities.PART,
    BIDSEntities.RECORDING: BIDSEntities.RECORDING,
    BIDSEntities.SPACE: BIDSEntities.SPACE,
    BIDSEntities.SUFFIX: BIDSEntities.SUFFIX,
    BIDSEntities.SCANS: BIDSEntities.SCANS,
    BIDSEntities.FMAP: BIDSEntities.FMAP,
    BIDSEntities.DATATYPE: BIDSEntities.DATATYPE,
    BIDSEntities.EXTENSION: BIDSEntities.EXTENSION,
}

# Entities for which variable collections can be extracted
BIDS_COLLECTION_ENTITIES = [BIDSEntities.RUN, BIDSEntities.SESSION, BIDSEntities.SUBJECT, DATASET]

class BIDSDatasetExtractor(DatasetMetadataExtractor):
    """
    Top level BIDS extractor class interfacing with metalad
    Inherits from metalad's DatasetMetadataExtractor class
    """

    def get_id(self) -> UUID:
        # Generated using V4 UUID: https://www.uuidgenerator.net/
        return UUID("a05726b7-86e0-408c-a0ef-08f3d85df47b")

    def get_version(self) -> str:
        return "0.0.1"

    def get_data_output_category(self) -> DataOutputCategory:
        return DataOutputCategory.IMMEDIATE

    def get_required_content(self):
        # TODO: logging
        for filename in REQUIRED_BIDS_FILES:
            rslt = self.dataset.get(filename, on_failure='ignore', return_type='list')
            if 'status' in rslt[0] and rslt[0]['status'] == 'impossible':
                # TODO: how to yield this as a result to be picked up by datalad's result renderer
                msg = f"The file '{filename}' should be part of the BIDS dataset in order for the 'bids_dataset' extractor to function correctly"
                print(msg)
                raise FileNotFoundError                
        return True

    def extract(self, _=None) -> ExtractorResult:
        # TODO: remove this call once https://github.com/datalad/datalad-metalad/issues/243 is fixed
        self.get_required_content()

        log_progress(
            lgr.info,
            'extractorsbidsdataset',
            f'Start bids_dataset metadata extraction from {self.dataset.path}',
            total=2,
            label='bids_dataset metadata extraction',
            unit=' Dataset',
        )

        return ExtractorResult(
            extractor_version=self.get_version(),
            extraction_parameter=self.parameter or {},
            extraction_success=True,
            datalad_result_dict={
                "type": "dataset",
                "status": "ok"
            },
            immediate_data=BIDSmeta(self.dataset).get_metadata())

class BIDSmeta(object):
    """
    The BIDS dataset metadata extractor class that does the work
    """

    def __init__(self, dataset) -> None:
        self.dataset = dataset

    def get_metadata(self):
        """
        Function to load BIDSLayout and run metadata extraction
        """
        # Check if derivatives are in BIDS dataset
        deriv_dir = Path(self.dataset.path) / 'derivatives'
        derivative_exist = deriv_dir.exists()
        # Call BIDSLayout with dataset path and derivatives boolean
        # TODO: handle case with amoty or nonexisting derivatives directory
        # TODO: decide what to do with meta_data from derivatives,
        # if anything at all
        bids = BIDSLayout(self.dataset.path, derivatives=derivative_exist)
        # bids = BIDSLayout(self.dataset.path)
        dsmeta = self._get_dsmeta(bids)

        log_progress(
            lgr.info,
            'extractorsbidsdataset',
            f'Finished bids_dataset metadata extraction from {self.dataset.path}'
        )
        return dsmeta

    def _get_dsmeta(self, bids):
        """
        Internal function to extract metadata from BIDSLayout
        STEPS:
        1. Extract metadata from `dataset_description.json`
        2. Extract README text
        3. Extract information about entities
        4. Extract variable collection information on multiple levels
           (dataset, subject, session, run). The dataset level
           collection will grab variables from participants.tsv
        5. Add context to metadata output
        """
        # STEP 1: Extract metadata from `dataset_description.json`
        metadata = self._get_bids_dsdescription(bids)
        # STEP 2: Extract README text
        metadata['description'] = self._get_bids_readme()
        # STEP 3: Extract information about entities and add to metadata 
        metadata['entities'] = self._get_bids_entities(bids)
        # STEP 4: Extract variable collection information on multiple levels
        metadata['variables'] = self._get_bids_variables(bids)
        # STEP 5: Add context to metadata output
        metadata['@context'] = BIDSCONTEXT        
        return metadata

    def _get_bids_dsdescription(self, bids):
        """"""
        # TODO: try except error handling
        dsdesc_dict = bids.get_dataset_description()
        # Map extracted dict keys to standard keys
        return {
            BIDS_PROPERTIES_MAPPING.get(k, k): v
            for k, v in dsdesc_dict.items()
        }

    def _get_bids_readme(self):
        """"""
        readme = []
        README_files = [file for file in Path(self.dataset.path).glob('README.*')]
        if len(README_files) > 0:
            for README_fname in README_files:
                self.dataset.get(README_fname)
                readme.append(get_text_from_file(README_fname))
        return readme if readme else None

    def _get_bids_entities(self, bids):
        """"""
        # Get dataset-specific entities from BIDSLayout
        ds_entities = list(bids.entities.keys())
        new_entities = {}
        # If the entity is in the main list AND in the list 
        # created from the dataset (i.e. in BIDSLayout),
        # the entity values can be retrieved using 
        # BIDSLayout.get_[entity]()
        for ent in BIDS_ENTITIES_MAPPING.keys():
            if ent in ds_entities:
                class_method = getattr(bids, f"get_{ent}")
                new_entities[ent] = class_method()
                # Delete key/value if value is empty list
                if not new_entities[ent]:
                    del(new_entities[ent])
        return new_entities

    def _get_bids_variables(self, bids):
        """"""
        # Extract variable collection information on multiple levels
        # levels (dataset, subject, session, run). The dataset level
        # collection will grab variables from participants.tsv
        variables  = {}
        for ent in BIDS_COLLECTION_ENTITIES:
            try:
                cols = bids.get_collections(level=ent)
                if cols:
                    variables[ent] = list(cols[0].to_df().columns)
            except Exception as e:
                # 'run' collection would require file content, i.e.
                # it will (intentionally) fail on a dataset-level
                pass
        return variables

# TODO: duplicate code from https://github.com/datalad/datalad-metalad/pull/242/commits/874e789a33778636f32594df49810b0baca124ca
# To be removed once PR is merged, and replaced by a function import from metalad.extractors.utils
def get_text_from_file(file_path:Path):
    """Return content of a text file as a string"""

    # TODO: check that file is text-based
    file_text = None
    try:
        with open(file_path) as f:
            file_text = ensure_unicode(f.read()).strip()
            return file_text
    except FileNotFoundError as e:
        # TODO: consider returning None in case of exception, depending
        # on what extractors would expect as default behaviour
        print((f'The provided file path could not be found: {str(file_path)}'))
        raise 