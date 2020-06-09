# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""MINC metadata extractor"""

import logging
lgr = logging.getLogger('datalad.metadata.extractors.minc')


from datalad.metadata.extractors.base import BaseMetadataExtractor
from minc2_simple import minc2_file


class MetadataExtractor(BaseMetadataExtractor):
    # this extractor instance knows:
    #   self.ds -- an instance of the dataset it shall operate on
    #   self.paths -- a list of paths within the dataset from which
    #                 metadata should be extracted, pretty much up to
    #                 the extractor if those those paths are used. They are
    #                 provided to avoid duplicate directory tree traversal
    #                 when multiples extractors are executed
    def get_metadata(self, dataset, content):
        files = []
        # We're only interested in files that look like minc files.
        for f in self.paths:
            if f.endswith(".mnc"):
                files.append(f)
        return {}, self.get_minc_metadata(files)

    def get_minc_metadata(self, files):
        for f in files:
            # Get all minc headers from the minc2 file.
            m = minc2_file(f)
            meta = m.metadata()

            # We need to convert our minc2-simple dictionary
            # to a version of the dictionary that works with
            # datalad. That means that the keys need to be strings,
            # not bytes, and that we strip out anything that isn't
            # hashable or decodeable, to ensure that we restrict
            # ourselves to headers that can be serialized to json.
            # Note that this only handles headers that are exactly
            # 2 deep.
            strmeta = {}
            for key in meta:
                # Convert the key from bytes to string so that datalad doesn't
                # die on key.startswith.
                kd = key.decode()
                strmeta[kd] = {}
                for subkey in meta[key]:
                    # Do the same for the subkeys.
                    skd = subkey.decode()
                    if meta[key][subkey].__hash__:
                        try:
                            # convert the value to utf-8. If it can't be converted
                            # to utf-8, it can't be serialized to JSON, so isn't indexable
                            # by datalad
                            v = meta[key][subkey]
                            encodedv = meta[key][subkey].decode('utf-8')
                            strmeta[kd][skd] = encodedv
                        except UnicodeDecodeError:
                            lgr.debug("Skipped %s.%s in %s" % (key, subkey, f,))
            yield f, strmeta
