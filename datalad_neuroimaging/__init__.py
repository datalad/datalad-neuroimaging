"""DataLad neuroimaging extension"""

__docformat__ = 'restructuredtext'

# defines a datalad command suite
# this symbold must be indentified as a setuptools entrypoint
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
            'datalad_neuroimaging.commands.create_study',
            'CreateStudy',
            'ni-create-study',
            'ni_create_study',
        ),
        (
            'datalad_neuroimaging.commands.import_dicoms',
            'ImportDicoms',
            'ni-import-dicomtarball',
            'ni_import_dicomtarball',
        ),
        (
            'datalad_neuroimaging.commands.dicom2spec',
            'Dicom2Spec',
            'ni-dicom2spec',
            'ni_dicom2spec',
        ),
    ]
)
