.. This file is auto-converted from CHANGELOG.md (make update-changelog) -- do not edit

Change log
**********
::

     ____            _             _                   _ 
    |  _ \    __ _  | |_    __ _  | |       __ _    __| |
    | | | |  / _` | | __|  / _` | | |      / _` |  / _` |
    | |_| | | (_| | | |_  | (_| | | |___  | (_| | | (_| |
    |____/   \__,_|  \__|  \__,_| |_____|  \__,_|  \__,_|
                                               Neuroimaging

This is a high level and scarce summary of the changes between releases.
We would recommend to consult log of the `DataLad git
repository <http://github.com/datalad/datalad-meuroimaging>`__ for more
details.

0.1 (Apr 28, 2018) -- The Release
---------------------------------

Major refactoring and deprecations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  This is the first separate release of DataLad's neuroimaging
   functionality as an extension module.
-  Metadata
-  BIDS metadata now uniformly refers to subjects and participants using
   the metadata key 'subject'

Enhancements and new features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Extractors now report progress (with DataLad 0.10+)
-  BIDS participant metadata is now read via pybids

Fixes
~~~~~

-  Fix issue with unicode characters in BIDS metadata
-  DICOM metadata now also contains the 'PatientName' field that was
   previously excluded due to a too restrictive data type filter
