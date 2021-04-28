# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""generate a GIN datacite.yml template from a BIDS dataset"""

__docformat__ = 'restructuredtext'

import json
import logging
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from datalad.distribution.dataset import require_dataset
from datalad.interface.base import Interface
from datalad.interface.base import build_doc
from datalad.support.param import Parameter
from datalad.distribution.dataset import Dataset, datasetmethod
from datalad.interface.utils import eval_results
from datalad.distribution.dataset import EnsureDataset
from datalad.support.constraints import EnsureNone


lgr = logging.getLogger("datalad.neuroimaging.bids2gindatacite")


class BIDSKeys:
    AUTHORS = "Authors"
    FUNDING = "Funding"
    LICENSE = "License"
    NAME = "Name"
    REFERENCESANDLINKS = "ReferencesAndLinks"


class GINEntries:
    AFFILIATION = "affiliation"
    AUTHORS = "authors"
    FIRST_NAME = "firstname"
    FUNDING = "funding"
    ID = "id"
    LAST_NAME = "lastname"
    LICENSE = "license"
    REFERENCES = "references"
    RESOURCE_TYPE = "resourcetype"
    TITLE = "title"


authors_header_template = """
# Automatically extracted author entries. Please provide affiliation
# and ID for each entry, if possible.
# "affiliation" is a free text string, e.g.,
# affiliation: "Some University, Southern Sea Islands".
# "id" can be any unique ID, including ORCID and ResearcherID.
# For an ORCID-ID use an "ORCID:"-prefix, e.g., "ORCID:0000-0001-2345-6789"
# For a ResearcherID use a "ResearcherID:"-prefix, e.g., "ResearcherID:X-1234-5678"
"""


authors_missing_template = """
# No authors given in 'dataset_description.json', but a
# GIN-Datacite-file (aka. datacite.yml) requires an author-entry.
# Please provide authors according to the following example
# (id and affiliation are not mandatory, but recommended).
# Example below:
#
# authors:
#   - firstname: "GivenName1"
#     lastname: "FamilyName1"
#     affiliation: "Affiliation1"
#     id: "ORCID:0000-0001-2345-6789"
# 
#   - firstname: "GivenName2"
#     lastname: "FamilyName2"
#     affiliation: "Affiliation2"
#     id: "ResearcherID:X-1234-5678"
# 
#   - firstname: "GivenName3"
#     lastname: "FamilyName3"
"""


description_missing_template = """
# A GIN-Datacite-file (aka. datacite.yml) requires a description-entry.
# Please provide a description of the resource. The description
# should provide additional information about the resource, e.g.,
# a brief abstract.
# Example below:

# description: |
#   Example of a description.
#   A description can contain linebreaks
#   but has to maintain indentation.
"""


funding_missing_template = """
# Please consider adding funding information.
# Example below:

# funding:
#   - "DFG, AB1234/5-6"
#   - "EU, EU.12345"
"""


keywords_missing_template = """
# Please provide a list of keywords the resource should be associated
# with. Give as many keywords as possible, to make the resource
# findable.
# Example below:

# keywords:
#   - Neuroscience
#   - Keyword2
#   - Keyword3
"""


license_missing_template = """
# GIN requires license information. Please provide the license
# name and/or a link to the license.
# Please add also a corresponding LICENSE file to the repository.
# Example below:

# license:
#   name: "Creative Commons CC0 1.0 Public Domain Dedication"
#   url: "https://creativecommons.org/publicdomain/zero/1.0/"
"""


references_and_links_missing_template = """
# Please consider adding references to related publications as
# described below:
# reftype might be: IsSupplementTo, IsDescribedBy, IsReferencedBy.
# Please provide digital identifier (e.g., DOI) if possible.
# Add a prefix to the ID, separated by a colon, to indicate the source.
# Supported sources are: DOI, arXiv, PMID
# In the citation field, please provide the full reference, including title, authors, journal etc.
# Example below:

# references:
#   - id: "doi:10.xxx/zzzz"
#     reftype: "IsSupplementTo"
#     citation: "Citation1"
#   - id: "arxiv:mmmm.nnnn"
#     reftype: "IsSupplementTo"
#     citation: "Citation2"
#   - reftype: "IsSupplementTo"
#     citation: "Citation3"
"""


@build_doc
class BIDS2GINDatacite(Interface):
    """Create a datacite.yml file from BIDS information"""

    _params_ = dict(
        dataset=Parameter(
            args=("-d", "--dataset"),
            doc="""BIDS-compatible dataset, for which the GIN-Datacite-file,
            aka "datacite.yml"-template should be created.
            If not dataset is given, an attempt is made to identify the dataset
            based on the current working directory.""",
            constraints=EnsureDataset() | EnsureNone()),
        output=Parameter(
            args=('--output',),
            doc="""Name of the generated Datacite-file (default: 
            "datacite.yml")"""),
        force=Parameter(
            args=("-f", "--force",),
            action="store_true",
            doc="""If this flag is set, overwrite an existing datacite.yml
            file"""),
    )

    @staticmethod
    @datasetmethod(name='bids2gindatacite')
    @eval_results
    def __call__(dataset=None,
                 output="datacite.yml",
                 force=False):

        if not isinstance(dataset, Dataset):
            dataset = Path(dataset or ".")

        dataset = require_dataset(
            dataset=dataset,
            purpose="read access",
            check_installed=True)

        dataset_description_path = dataset.pathobj / "dataset_description.json"
        if not dataset_description_path.exists():
            yield dict(
                action='bids2gindatacite',
                logger=lgr,
                message="could not find dataset description file "
                        f"({dataset_description_path}). Is the dataset at "
                        f"{dataset.path} BIDS-compliant?",
                path=str(dataset_description_path),
                status="error"
            )
            return

        with dataset_description_path.open(mode="rt") as f:
            dataset_description_object = json.load(f)

        datacite_file_path = dataset.pathobj / output
        if datacite_file_path.exists() and force is False:
            yield dict(
                action='bids2gindatacite',
                logger=lgr,
                message=f"File {datacite_file_path} already exists. If you want "
                        f"to override the existing file, specify -f/--force.",
                path=str(datacite_file_path),
                status="error"
            )
            return

        for result in generate_gin_datacite_file(
                dataset_description_object,
                datacite_file_path):
            yield {
                **dict(
                    action='bids2gindatacite',
                    logger=lgr,
                    path=str(dataset_description_path)),
                **result
            }

        return


def generate_gin_datacite_file(dataset_description_object: dict,
                               datacite_file_path: Path) -> Iterable:

    error_generated = False
    result = []
    for line_generator in (generate_authors,
                           generate_title,
                           generate_description,
                           generate_keywords,
                           generate_license,
                           generate_funding,
                           generate_references,
                           generate_resource_type):

        lines, error = line_generator(dataset_description_object)
        if error:
            error_generated = True
            yield error
        else:
            result.extend(lines + [""])

    if not error_generated:
        datacite_file_path.write_text("\n".join(result) + "\n")


def generate_authors(dataset_description_obj: dict
                     ) -> Tuple[Optional[List[str]], Optional[dict]]:

    authors = dataset_description_obj.get(BIDSKeys.AUTHORS, None)
    if authors is None:
        lgr.debug(f"'{BIDSKeys.AUTHORS}' missing in dataset description")
        return [authors_missing_template], None

    result = [
        authors_header_template,
        f"{GINEntries.AUTHORS}:"]

    for author in authors:
        if author.count(",") == 1:
            last_name, first_name = author.split(",")
        else:
            elements = author.split()
            if len(elements) > 1:
                first_name = " ".join(elements[:-1])
                last_name = elements[-1]
            else:
                first_name = "<unknown>"
                last_name = elements[0]
        result.extend([
            f'  # GENERATED FROM: {BIDSKeys.AUTHORS}-entry: "{author}"',
            f'  - {GINEntries.FIRST_NAME}: {first_name}',
            f'    {GINEntries.LAST_NAME}: {last_name}',
            f'    # {GINEntries.AFFILIATION}: "<unknown>"',
            f'    # {GINEntries.ID}: "<unknown>"',
        ])

    return result, None


def generate_title(dataset_description_obj: dict
                   ) -> Tuple[Optional[List[str]], Optional[dict]]:

    name = dataset_description_obj.get(BIDSKeys.NAME, None)
    if name is None:
        return None, dict(
        message=f"required key {BIDSKeys.NAME} not found in "
                f"'dataset_description.json'",
        status="error")

    return [
        f"# GENERATED from dataset_description.json#{BIDSKeys.NAME}",
        f'{GINEntries.TITLE}: "{name}"'
    ], None


def generate_description(dataset_description_obj: dict
                         ) -> Tuple[Optional[List[str]], Optional[dict]]:

    return [description_missing_template], None


def generate_keywords(dataset_description_obj: dict
                      ) -> Tuple[Optional[List[str]], Optional[dict]]:
    return [keywords_missing_template], None


def generate_license(dataset_description_obj: dict
                     ) -> Tuple[Optional[List[str]], Optional[dict]]:

    license = dataset_description_obj.get(BIDSKeys.LICENSE, None)
    if license is None:
        lgr.debug(
            f"No {BIDSKeys.LICENSE}-key found in 'dataset_description.json'")
        return [license_missing_template], None

    return [
        f'# GENERATED FROM: {BIDSKeys.LICENSE}: "{license}"',
        f'# If possible, please provide a link to the license in the url-entry.',
        f'# Please add also a corresponding LICENSE file to the repository.',
        f'license:',
        f'  name: "{license}"',
        f'  # url: "https://creativecommons.org/publicdomain/zero/1.0/"'
    ], None


def generate_funding(dataset_description_obj: dict
                     ) -> Tuple[Optional[List[str]], Optional[dict]]:

    funding = dataset_description_obj.get(BIDSKeys.FUNDING, None)
    if funding is None:
        lgr.debug(
            f"No {BIDSKeys.FUNDING}-field found in 'dataset_description.json'")
        return [funding_missing_template], None

    else:
        if not isinstance(funding, List):
            lgr.warning(
                f"{BIDSKeys.FUNDING}-field in 'dataset_description.json' "
                f"does not contain an arry, ignoring it.")
            return [funding_missing_template], None

        result = [f"{GINEntries.FUNDING}:"]
        for funder in funding:
            result.extend([
                f"# GENERATED FROM: {BIDSKeys.FUNDING}-entry: {funder} in 'dataset_description.json'",
                f'  - "{funder}"'
            ])

    return result, None


def generate_references(dataset_description_obj: dict
                        ) -> Tuple[Optional[List[str]], Optional[dict]]:

    references_and_links = dataset_description_obj.get(
        BIDSKeys.REFERENCESANDLINKS,
        None)

    if references_and_links is None:
        lgr.debug(
            f"No {BIDSKeys.FUNDING}-key found in 'dataset_description.json'")
        return [references_and_links_missing_template], None

    else:
        if not isinstance(references_and_links, List):
            lgr.warning(
                f"{BIDSKeys.REFERENCESANDLINKS}-field in "
                f"'dataset_description.json' does not contain an arry, "
                f"ignoring it.")
            return [references_and_links_missing_template], None

        result = []
        references = []
        for reference_or_link in references_and_links:
            if reference_or_link.startswith("http://") or reference_or_link.startswith("https://"):
                result.append(
                    f"# ignoring {BIDSKeys.REFERENCESANDLINKS}-entry "
                    f"{reference_or_link}, because it is a link.")
                continue
            references.append(reference_or_link)

        if references:
            result.append(f"{GINEntries.REFERENCES}:")
            for reference in references:
                result.extend([
                    f"  # GENERATED FROM: {BIDSKeys.REFERENCESANDLINKS}-entry: "
                    f"{reference} in 'dataset_description.json'",
                    f'  - reftype: "IsSupplementTo"',
                    f'    citation: "{reference}"',
                    f'    # id: <not set, please provide if possible>'
                ])

    return result, None


def generate_resource_type(dataset_description_obj: dict
                           ) -> Tuple[Optional[List[str]], Optional[dict]]:
    return [
        f"{GINEntries.RESOURCE_TYPE}: Dataset"
    ], None
