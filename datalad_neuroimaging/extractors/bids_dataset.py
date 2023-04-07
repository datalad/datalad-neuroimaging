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
from pathlib import Path
from uuid import UUID

from bids import BIDSLayout
from datalad.log import log_progress
from datalad.utils import ensure_unicode
from datalad_metalad.extractors.base import (
    DataOutputCategory,
    DatasetMetadataExtractor,
    ExtractorResult,
)
from datalad_deprecated.metadata.definitions import vocabulary_id


lgr = logging.getLogger("datalad.metadata.extractors.bids_dataset")


class BIDSProperties:
    """Main properties used in BIDS v1.6.0 dataset description"""
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


class BIDSEntities:
    """Main entities used in BIDS v1.6.0 filenames"""
    SUBJECT = "subject"
    SESSION = "session"
    TASK = "task"
    ACQUISITION = "acquisition"
    CEAGENT = "ceagent"
    RECONSTRUCTION = "reconstruction"
    DIRECTION = "direction"
    RUN = "run"
    PROC = "proc"
    MODALITY = "modality"
    ECHO = "echo"
    FLIP = "flip"
    INV = "inv"
    MT = "mt"
    PART = "part"
    RECORDING = "recording"
    SPACE = "space"
    SUFFIX = "suffix"
    SCANS = "scans"
    FMAP = "fmap"
    DATATYPE = "datatype"
    EXTENSION = "extension"


BIDSCONTEXT = {
    "@id": "https://doi.org/10.5281/zenodo.4710751",
    "description": "ad-hoc vocabulary for the Brain Imaging Data Structure (BIDS) standard v1.6.0",
    "type": vocabulary_id,
}

REQUIRED_BIDS_FILES = ["dataset_description.json"]

DATASET = "dataset"

# The following mappings are one-to-one currently, but could change in future
BIDS_PROPERTIES_MAPPING = {
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

# Entities for which variable collections can be extracted without requiring
# file content
BIDS_COLLECTION_ENTITIES = [
    BIDSEntities.RUN,
    BIDSEntities.SESSION,
    BIDSEntities.SUBJECT,
    DATASET,
]


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
        # bids_dir = _find_bids_root(self.dataset.path)
        for f in REQUIRED_BIDS_FILES:
            f_abs = self.dataset.pathobj / f
            if f_abs.exists() or f_abs.is_symlink():
                result = self.dataset.get(f_abs, result_renderer="disabled")
                failure_count = 0
                for res in result:
                    if res["status"] in ("error", "impossible"):
                        failure_count += 1
                if failure_count > 0:
                    yield dict(
                        path=self.dataset.path,
                        action="meta_extract",
                        type="dataset",
                        status="error",
                        message=("required file content not retrievable: %s", f),
                    )
                else:
                    yield dict(
                        path=self.dataset.path,
                        action="meta_extract",
                        type="dataset",
                        status="ok",
                        message=("required file(s) retrieved"),
                    )
            else:
                yield dict(
                    path=self.dataset.path,
                    action="meta_extract",
                    type="dataset",
                    status="impossible",
                    message=(
                        "metadata source is not available in %s: %s",
                        self.dataset.path,
                        f,
                    ),
                )
        return

    def extract(self, _=None) -> ExtractorResult:
        log_progress(
            lgr.info,
            "extractorsbidsdataset",
            f"Start bids_dataset metadata extraction from {self.dataset.path}",
            total=1,
            label="bids_dataset metadata extraction",
            unit=" Dataset",
        )
        return ExtractorResult(
            extractor_version=self.get_version(),
            extraction_parameter=self.parameter or {},
            extraction_success=True,
            datalad_result_dict={"type": "dataset", "status": "ok"},
            immediate_data=BIDSmeta(self.dataset).get_metadata(),
        )


class BIDSmeta(object):
    """
    The extractor class for BIDS dataset-level metadata

    Extracts dataset-level metadata of a BIDS-compliant dataset, using
    PyBIDS
    """

    def __init__(self, dataset) -> None:
        self.dataset = dataset

    def get_metadata(self):
        """
        Function to load BIDSLayout and trigger metadata extraction
        """
        bids_dir = _find_bids_root(self.dataset.path)
        # Check if derivatives are in BIDS dataset
        deriv_dir = bids_dir / "derivatives"
        derivative_exist = deriv_dir.exists()
        # TODO: handle case with amoty or nonexisting derivatives directory
        # TODO: decide what to do with meta_data from derivatives, if anything
        # Call BIDSLayout with dataset path and derivatives boolean
        bids = BIDSLayout(bids_dir, derivatives=derivative_exist)
        dsmeta = self._get_dsmeta(bids)
        log_progress(
            lgr.info,
            "extractorsbidsdataset",
            f"Finished bids_dataset metadata extraction from {bids_dir}",
        )
        return dsmeta

    def _get_dsmeta(self, bids):
        """
        Internal function to extract metadata from pyBIDS' BIDSLayout
        
        This function executes the following steps:
        1. Extract metadata from `dataset_description.json`
        2. Extract README text
        3. Extract information about entities
        4. Extract variable collection information on multiple levels
           (dataset, subject, session, run). The dataset level
           collection will grab variables from participants.tsv if
           available.
        5. Add context to metadata output
        """
        # STEP 1: Extract metadata from `dataset_description.json`
        metadata = self._get_bids_dsdescription(bids)
        # STEP 2: Extract README text
        metadata["description"] = self._get_bids_readme()
        # STEP 3: Extract information about entities and add to metadata
        metadata["entities"] = self._get_bids_entities(bids)
        # STEP 4: Extract variable collection information on multiple levels
        metadata["variables"] = self._get_bids_variables(bids)
        # STEP 5: Add context to metadata output
        metadata["@context"] = BIDSCONTEXT
        return metadata

    def _get_bids_dsdescription(self, bids):
        """Get BIDS dataset description"""
        # Get info from 'dataset_description.json'
        dsdesc_dict = bids.get_dataset_description()
        # Map extracted dict keys to standard keys
        return {BIDS_PROPERTIES_MAPPING.get(k, k): v for k, v in dsdesc_dict.items()}

    def _get_bids_readme(self):
        """Get text from README, if any"""
        readme = []
        # Grab all readme files, loop through
        for README_fname in [
            file for file in Path(self.dataset.path).glob("[Rr][Ee][Aa][Dd][Mm][Ee]*")
        ]:
            # datalad get content if annexed
            self.dataset.get(README_fname)
            # read text from file
            try:
                file_text = ensure_unicode(README_fname.read_text()).strip()
            except:
                file_text = ""
            # Append dict with file text + extension to list
            readme.append({"extension": README_fname.suffix, "text": file_text})
        return readme if readme else None

    def _get_bids_entities(self, bids):
        """Get dataset-specific entities from BIDSLayout"""
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
                    del new_entities[ent]
        return new_entities

    def _get_bids_variables(self, bids):
        """Get variable collection information from BIDSLayout"""
        # Extract variable collection information on multiple levels
        # levels (dataset, subject, session, run). The dataset level
        # collection will grab variables from participants.tsv if
        # available
        variables = {}
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


def _find_bids_root(dataset_path) -> Path:
    """
    Find relative location of BIDS directory within datalad dataset
    """
    description_paths = list(Path(dataset_path).glob("**/dataset_description.json"))
    # 1 - if more than one, select first and output warning
    # 2 - if zero, output error
    # 3 - if 1, add to dataset path and set ats bids root dir
    if len(description_paths) == 0:
        msg = ("The file 'dataset_description.json' should be part of the BIDS dataset "
        "in order for the 'bids_dataset' extractor to function correctly")
        raise FileNotFoundError(msg)
    elif len(description_paths) > 1:
        msg = (f"Multiple 'dataset_description.json' files ({len(description_paths)}) "
        f"were found in the recursive filetree of {dataset_path}, selecting "
        "first path.")
        lgr.warning(msg)
        return Path(description_paths[0]).parent
    else:
        return Path(description_paths[0]).parent
