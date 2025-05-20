"""DataLad neuroimaging extension"""

__docformat__ = 'restructuredtext'

from .version import __version__

# defines a datalad command suite
# this symbold must be identified as a setuptools entrypoint
# to be found by datalad
command_suite = (
    # description of the command suite, displayed in cmdline help
    "Neuroimaging tools",
    [
        # specification of a command, any number of commands can be defined
        (
            # importable module that contains the command implementation
            'datalad_neuroimaging.bids2scidata',
            # name of the command class implementation in above module
            'BIDS2Scidata',
            'bids2scidata',
        ),
        (
            'datalad_neuroimaging.bids2gindatacite',
            'BIDS2GINDatacite',
            'bids2gindatacite',
        ),
    ]
)

from . import _version

__version__ = _version.get_versions()['version']
