# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""FSL Feat analysis configuration and result metadata extractor"""
from __future__ import absolute_import

from os.path import join as opj
from os.path import exists
from os.path import basename
from os.path import dirname
from os.path import relpath
import re
import logging
lgr = logging.getLogger('datalad.metadata.extractors.fslfeat')
from datalad.log import log_progress
from datalad.metadata.definitions import vocabulary_id
from datalad.metadata.extractors.base import BaseMetadataExtractor


context = {
    'fslfeat': {
        # no term definitions exists for FEAT's variable names
        # going with a disambiguating URL for now
        '@id': 'https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FEAT/',
        'description': 'non-vocabulary for FSL FEAT variables',
        'type': vocabulary_id}
}

_contrastvar_expr = re.compile(r'([^\d]+)([\d]+)\.([\d]+)')

_procedural_switches = {
    'tsplot_yn', 'poststats_yn', 'melodic_yn', 'stats_yn',
    'regstandard_yn', 'regstandard_nonlinear_yn', 'filtering_yn',
}

_ignor_vars = {
    'fmri(relative_yn)', 'fmri(help_yn)', 'fmri(featwatcher_yn)',
    'fmri(sscleanup_yn)', 'fmri(zdisplay)', 'fmri(zmin)',
    'fmri(zmax)', 'fmri(rendertype)', 'fmri(bgimage)',
    'fmri(constcol)',
}

_trancode = {
    'analysis': {
        '0': 'nofirstlevel',
        '7': 'full',
        '1': 'preprocessing',
        '2': 'statistics',
    },
    'level': {
        '1': 'first',
        '2': 'higher',
    },
    'inputtype': {
        '1': 'featdir',
        '2': 'cope',
    },
    'mc': {
        '0': 'none',
        '1': 'mcflirt',
    },
    'st': {
        '0': 'none',
        '1': 'regularup',
        '2': 'regulardown',
        '3': 'sliceordercfgfile',
        '4': 'slicetimingcfgfile',
        '5': 'interleaved',
    },
    'motionevs': {
        '0': False,
        '1': True,
    },
    'mixed_yn': {
        '0': 'me_ols',
        '1': 'me_flame1+2',
        '2': 'me_flame1',
        '3': 'fixedeffects',
    },
    'thresh': {
        '0': 'none',
        '1': 'uncorrected',
        '2': 'voxel',
        '3': 'cluster',
    },
    'tempfilt_yn': {
        '0': False,
        '1': True,
    },
    'shape': {
        '0': 'square',
        '1': 'sinusoid',
        '2': 'custom_ev1',
        '3': 'custom_ev3',
        '4': 'interaction',
        '10': 'empty',
    },
}


def _convert_dtype(val):
    if isinstance(val, (bool, int, float)):
        return val
    try:
        return int(val)
    except:
        try:
            return float(val)
        except:
            return val


def _read_fsf(path, dspath):
    props = {}
    evs = {}
    contrasts = {}
    disabled = set()
    valid_props = {}
    for line in open(path):
        if not line.startswith('set '):
            continue
        cmd, var = line.split()[:2]
        # TODO match feat_files(...) to get input fMRI data
        if not (cmd == 'set' and var.startswith('fmri(') and var.endswith(')')):
            lgr.debug(
                'Ignoring unknown/malformed setting from %s: %s',
                path, line)
            continue
        if var in _ignor_vars or var.startswith('fmri(conpic_'):
            continue
        # cut out value, strip whitespace around, and shed quotes
        val = line[5 + len(var):].strip().strip('"')
        # strip common 'fmri(xxx)'
        var = var[5:-1]
        store_in = props
        if var[-1].isdigit() and '.' not in var and not var.startswith('conmask'):
            ev_id = int(var[-1])
            # this is a variable describing an EV
            store_in = evs.get(ev_id, {})
            evs[ev_id] = store_in
            var = var[:-1]
        if val.startswith(dspath):
            val = relpath(val, start=dspath)
        # transcode values on a best-effort basis
        val = _trancode.get(var, {}).get(val, val)
        # final dtype
        val = _convert_dtype(val)
        if var in _procedural_switches:
            if val == 0:
                disabled.add(var)
            continue
        if var in ('evs_orig', 'evs_real'):
            valid_props[var] = int(val)
        if var.endswith('_yn'):
            var = var[:-3]
        if val == '':
            continue
        # handle specification of vector elements
        vecvals = _contrastvar_expr.match(var)
        if vecvals:
            name, con, pos = vecvals.groups()
            pos = int(pos)
            con = int(con)
            if name == 'ortho':
                if pos == 0:
                    # XXX this is a bit strange, there is not EV0
                    continue
                rec = evs.get(con, {})
                vec = rec.get(name, [0] * valid_props['evs_orig'])
            else:
                rec = contrasts.get(con, {})
                vec = rec.get(
                    name,
                    [0] * valid_props['evs_real' if '_real' in name else 'evs_orig'])
            vec[pos - 1] = val
            rec[name] = vec
            if name == 'ortho':
                evs[con] = rec
            else:
                contrasts[con] = rec
            continue
        if var.startswith('conname_'):
            # contrast names
            con = int(var.split('.')[-1])
            rec = contrasts.get(con, {})
            rec['name'] = val
            contrasts[con] = rec
            continue

        store_in[var] = val
    # clean-up
    for ev in evs.values():
        # shed orthogonalization cfg, if noe was performed
        if 'ortho' in ev and all(i == 0 for i in ev['ortho']):
            ev.pop('ortho')
    props['ev'] = [evs[i] for i in sorted(evs, key=lambda x: int(x))]
    props['contrasts'] = [contrasts[i]
                          for i in sorted(contrasts, key=lambda x: int(x))]
    # TODO filter out all variables related to steps that were not
    # performed
    props['steps_disabled'] = [s if not s.endswith('_yn') else s[:-3]
                               for s in sorted(disabled)]

    # TODO make absolute paths relative to the dataset root
    return props


class MetadataExtractor(BaseMetadataExtractor):

    _unique_exclude = {
    }

    def get_metadata(self, dataset, content):
        analyses = []
        log_progress(
            lgr.info,
            'extractorfslfeat',
            'Start FSL Feat metadata extraction from %s', self.ds,
            total=len(self.paths),
            label='FSL Feat metadata extraction',
            unit=' Files',
        )
        for f in self.paths:
            absfp = opj(self.ds.path, f)
            log_progress(
                lgr.info,
                'extractorfslfeat',
                'Extract FSL Feat metadata from %s', absfp,
                update=1,
                increment=True)

            if not basename(f) == 'design.fsf':
                # ignore everything else. any analysis must have this, even if
                # it never ran and has no results
                lgr.debug("Ignoring non-analysis configuration %s", f)
                continue

            analysis_path = dirname(f)
            analysis = {
                'path': analysis_path,
            }
            analysis.update(_read_fsf(absfp, self.ds.path))

            # look for per-contrast result tables
            for i, rec in enumerate(analysis.get('contrasts', [])):
                clustertable_fname = opj(
                    self.ds.path, analysis_path, 'cluster_zstat{}.txt'.format(i + 1))
                if exists(clustertable_fname):
                    import pandas as pd
                    df = pd.read_csv(
                        clustertable_fname,
                        sep='\t',
                    )
                    rec['clusters'] = df.to_dict(orient='records')

            analyses.append(analysis)

        log_progress(
            lgr.info,
            'extractorfslfeat',
            'Finished FSL Feat metadata extraction from %s', self.ds
        )

        dsmeta = {
            '@context': context,
            'analysis': analyses,
        }
        return (
            dsmeta,
            []
        )
