# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""NIDM metadata extractor"""

import logging
import os.path as op
from zipfile import ZipFile

from datalad.dochelpers import exc_str
from datalad.support import json_py

lgr = logging.getLogger('datalad.metadata.extractors.nidmresults')

from datalad.metadata.definitions import vocabulary_id
from datalad.metadata.extractors.base import BaseMetadataExtractor

from datalad.support.network import is_url


class MetadataExtractor(BaseMetadataExtractor):

    def get_metadata(self, dataset, content):
        # function gets two flags indicating whether to extract dataset-global
        # and/or content metadata

        # function returns a tuple
        # item 1: dict with dataset-global metadata
        #         should come with a JSON-LD context for that blob, context
        #         is preserved during aggregation
        # item 2: generator yielding metadata dicts for each (file) path in the
        #         dataset. When querying aggregated metadata for a file, the dataset's
        #         JSON-LD context is assigned to the metadata dict, hence file metadata
        #         should not be returned with individual/repeated contexts, but rather
        #         the dataset-global context should provide all definitions

        # TODO we could report basic info on the dataset level too (maybe at least
        # number of analyses reported)
        # TODO agree on, and report a @context for the packs that are reported as content
        # metadata
        return \
            {}, \
            (self._yield_nidm_blobs() if content else [])

    def _yield_nidm_blobs(self):
        context_cache = {}

        for packfile in [f for f in self.paths if f.endswith('.nidm.zip')]:
            nidmblob = None
            try:
                packabspath = op.join(self.ds.path, packfile)
                with ZipFile(packabspath, 'r') as z:
                    nidmblob = z.read('nidm_minimal.json')
                nidmblob = json_py.loads(nidmblob)
            except Exception as e:
                lgr.warning(
                    "Failed to load NIDM results pack at %s: %s",
                    packabspath, exc_str(e))
                continue
            if isinstance(nidmblob, list):
                if len(nidmblob) == 1:
                    nidmblob = nidmblob[0]
                else:
                    lgr.warning(
                        "Found more then one NIDM result structure in pack at %s, cannot report that.",
                        packabspath)
                    continue

            context_url = nidmblob.get('@context', None)
            # TODO this conditional may go away if the final NIDM metadata concept
            # includes the full context and does not use a URL reference
            if context_url:
                # context might be a URL, in which case we want to capture the
                # actual context behind that URL, even if it is just the first
                # level
                if is_url(context_url) and context_url not in context_cache:
                    import requests
                    r = requests.get(context_url)
                    if r.ok:
                        # because if not, we just keep the URL as is
                        # (maybe a place holder ...)
                        context = r.json()
                        context_cache[context_url] = context

                nidmblob['@context'] = context_cache.get(
                    context_url, nidmblob['@context'])

            yield packfile, nidmblob
