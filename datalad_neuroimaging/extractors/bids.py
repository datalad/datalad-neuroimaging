# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""BIDS metadata extractor (http://bids.neuroimaging.io)"""

from __future__ import absolute_import
from math import isnan

# use pybids to evolve with the standard without having to track it too much
import bids
from bids import BIDSLayout

import re
from io import open
from os.path import join as opj
from os.path import exists
from os.path import curdir
from datalad.dochelpers import exc_str
from datalad.metadata.extractors.base import BaseMetadataExtractor
from datalad.metadata.definitions import vocabulary_id
from datalad.utils import assure_unicode
from datalad.support.external_versions import external_versions

from datalad import cfg

import logging
lgr = logging.getLogger('datalad.metadata.extractors.bids')
from datalad.log import log_progress


vocabulary = {
    # characteristics (metadata keys)
    "age(years)": {
        '@id': "pato:0000011",
        'unit': "uo:0000036",
        'unit_label': "year",
        'description': "age of a sample (organism) at the time of data acquisition in years"},
}

content_metakey_map = {
    # go with plain 'id' as BIDS has this built-in conflict of subject/participant
    # for the same concept
    'participant_id': 'id',
    'age': 'age(years)',
}

sex_label_map = {
    'f': 'female',
    'm': 'male',
}


class MetadataExtractor(BaseMetadataExtractor):
    _dsdescr_fname = 'dataset_description.json'

    _key2stdkey = {
        'Name': 'name',
        'License': 'license',
        'Authors': 'author',
        'ReferencesAndLinks': 'citation',
        'Funding': 'fundedby',
        'Description': 'description',
    }

    def get_metadata(self, dataset, content):
        derivative_exist = exists(opj(self.ds.path, 'derivatives'))
        bids = BIDSLayout(self.ds.path, derivatives=derivative_exist)

        dsmeta = self._get_dsmeta(bids)

        if not content:
            return dsmeta, []

        return dsmeta, self._get_cnmeta(bids)

    def _get_dsmeta(self, bids):
        context = {}
        meta = {self._key2stdkey.get(k, k): v
                for k, v in bids.get_metadata(
                    opj(self.ds.path, self._dsdescr_fname)).items()}

        # TODO maybe normalize labels of standard licenses to definition URIs
        # perform mapping

        README_fname = opj(self.ds.path, 'README')
        if not meta.get('description') and exists(README_fname):
            # BIDS uses README to provide description, so if was not
            # explicitly provided to possibly override longer README, let's just
            # load README
            with open(README_fname, 'rb') as f:
                desc = assure_unicode(f.read())
            meta['description'] = desc.strip()

        # special case
        # Could be None which we can't strip so or ''
        bids_version = (meta.get('BIDSVersion', '') or '').strip()
        bids_defurl = 'http://bids.neuroimaging.io'
        if bids_version:
            bids_defurl += '/bids_spec{}.pdf'.format(bids_version)
        meta['conformsto'] = bids_defurl
        context['bids'] = {
            # not really a working URL, but BIDS doesn't provide term defs in
            # any accessible way
            '@id': '{}#'.format(bids_defurl),
            'description': 'ad-hoc vocabulary for the Brain Imaging Data Structure (BIDS) standard',
            'type': vocabulary_id,
        }
        context.update(vocabulary)
        meta['@context'] = context
        return meta

    def _get_cnmeta(self, bids):
        # TODO any custom handling of participants infos should eventually
        # be done by pybids in one way or another
        path_props = {}
        participants_fname = opj(self.ds.path, 'participants.tsv')
        if exists(participants_fname):
            try:
                for rx, info in yield_participant_info(bids):
                    path_props[rx] = {'subject': info}
            except Exception as exc:
                if isinstance(exc, ImportError):
                    raise exc
                lgr.warning(
                    "Failed to load participants info due to: %s. Skipping the rest of file",
                    exc_str(exc)
                )

        log_progress(
            lgr.info,
            'extractorbids',
            'Start BIDS metadata extraction from %s', self.ds,
            total=len(self.paths),
            label='BIDS metadata extraction',
            unit=' Files',
        )
        # now go over all files in the dataset and query pybids for its take
        # on each of them
        for f in self.paths:
            absfp = opj(self.ds.path, f)
            log_progress(
                lgr.info,
                'extractorbids',
                'Extract BIDS metadata from %s', absfp,
                update=1,
                increment=True)
            # BIDS carries a substantial portion of its metadata in JSON
            # sidecar files. we ignore them here completely
            # this might yield some false-negatives in theory, but
            # this case has not been observed in practice yet, hence
            # doing it cheap for now
            if f.endswith('.json'):
                continue
            md = {}
            try:
                md.update(
                    {k: v
                     for k, v in bids.get_metadata(
                         opj(self.ds.path, f),
                         include_entities=True).items()
                     # no nested structures for now (can be monstrous when DICOM
                     # metadata is embedded)
                     if not isinstance(v, dict)})
            except ValueError as e:
                lgr.debug(
                    'PyBIDS errored on file %s in %s: %s '
                    '(possibly not BIDS-compliant or not recognized',
                    f, self.ds, exc_str(e))
                lgr.debug('no usable BIDS metadata for %s in %s: %s',
                          f, self.ds, exc_str(e))
                # do not raise here:
                # https://github.com/datalad/datalad-neuroimaging/issues/34
            except Exception as e:
                lgr.debug('no usable BIDS metadata for %s in %s: %s',
                          f, self.ds, exc_str(e))
                if cfg.get('datalad.runtime.raiseonerror'):
                    raise

            # no check al props from other sources and apply them
            for rx in path_props:
                if rx.match(f):
                    md.update(path_props[rx])
            yield f, md
        log_progress(
            lgr.info,
            'extractorbids',
            'Finished BIDS metadata extraction from %s', self.ds
        )


def yield_participant_info(bids):
    for bidsvars in bids.get_collections(
            level='dataset')[0].to_df().to_dict(orient='records'):
        props = dict(id=assure_unicode(bidsvars.pop('subject')))
        for p in bidsvars:
            # take away some ambiguity
            normk = assure_unicode(p).lower()
            hk = content_metakey_map.get(normk, normk)
            val = assure_unicode(bidsvars[p])
            if hk in ('sex', 'gender'):
                if hasattr(val, 'lower'):
                    val = val.lower()
                elif isinstance(val, float) and isnan(val):
                    # pybids reports 'n/a' is NaN
                    val = 'n/a'
                val = sex_label_map.get(val, val)
            if hk == 'suffix' and val == 'participants':
                # regression in PyBIDS 0.7.1, should be fixed in 0.8
                # https://github.com/bids-standard/pybids/issues/380
                # TODO: remove workaround whenever we depend on pybids >= 0.8
                #  after verifying that it is not succeptable
                continue
            if val:
                props[hk] = val
        if props:
            yield re.compile(r'^sub-{}/.*'.format(props['id'])), props
