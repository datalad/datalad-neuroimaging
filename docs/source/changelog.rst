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
repository <http://github.com/datalad/datalad-neuroimaging>`__ for more
details.

0.3.4 (Oct 24, 2023) – Make BIDS great again
--------------------------------------------

-  BIDS metadata extractor(s): do not require ``participants.tsv`` file
   to be present (it is RECOMMENDED not REQUIRED in BIDS)
-  ``cfg_bids`` procedure: do not annex any ``README*``, ``LICENSE``, or
   ``.bids-validator-config.json`` files
-  documentation: fix builds on RTD

0.3.3 (Oct 28, 2022) – Oktoberfest
----------------------------------

-  raise dependency on datalad-deprecated which was prematurely released

0.3.2 (Oct 25, 2022) – … but grandparents always are
----------------------------------------------------

-  increase dependency on datalad to 0.16.7
-  depend on datalad-metalad and datalad-deprecated for both styles of
   metadata extractors
-  update the metadata extractors to work with current numpy versions
-  BIDS extractor compatible with pybids>=0.15.1 and BIDS v1.6.0
-  fix nifti1 metadata extractor not dealing properly with byte strings
-  various internal changes and fixes around testing and CI setup

0.3.1 (Jun 3, 2020) – Uncles aren’t always nice either
------------------------------------------------------

-  be compatible with pydicom 2.0.0

0.3.0 (Feb 26, 2020) – … and parents become grumpier
----------------------------------------------------

-  DataLad 0.12 series is now minimal supported

0.2.4 (Feb 05, 2020) – Kids are growing
---------------------------------------

Minor bugfix release to account for changes in pybids and datalad

-  pybids:

   -  demand pybids >=0.9.2
   -  account for new field “extension” provided by BIDS now
   -  use get_dataset_description if available

-  pandas:

   -  use .iloc instead of deprecated .ix

-  datalad

   -  use -d^ instead of deprecated (in 0.12) -S in an example script

0.2.3 (May 24, 2019) – Old is not bad
-------------------------------------

Minor quick bugfix release to demand pybids < 0.9 since we are not yet
fully ready for its full glory

0.2.2 (May 20, 2019) – It was like that way before!
---------------------------------------------------

Minor bugfix release - revert back to old ways of installing package
data so test data and procedures get properly installed

0.2.1 (May 17, 2019) – Why wasn’t it that way before?
-----------------------------------------------------

-  include a procedure ‘cfg_bids’ to configure BIDS datasets
-  fix several issues with troublesome dependency declarations

0.2.0 (Feb 09, 2019) – Am I compatible with you honey?
------------------------------------------------------

-  Make compatible with (and demand) pybids 0.7.{0,1}. 0.7.0 introduced
   change of terms: modality -> suffix, and type -> datatype, which
   would now require to either reaggregate all previous metadata or
   somehow fixup in-place existing metadata files. And for 0.7.1
   workaround was added to not return ``suffix`` at least when
   participants.tsv was queried.
-  Make compatible with pydicom 1.0 in treatment of MultiValue
-  Refactorings:

   -  tests:

      -  use ``export_archive`` instead of plain ``tarfile.open``
      -  make compatible with recent (0.11.x) DataLad which now extract
         annex keys etc

0.1.5 (Sep 28, 2018) – BIDS robustness
--------------------------------------

-  Assorted improvements of the BIDS metadata extractor performance on
   datasets in the wild.

0.1.4 (Aug 02, 2018) – PyBIDS
-----------------------------

-  Fixed compatibility with pybids 0.6.4 and now demand it as the
   minimal PyBIDS version

0.1 (Apr 28, 2018) – The Release
--------------------------------

Major refactoring and deprecations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  This is the first separate release of DataLad’s neuroimaging
   functionality as an extension module.
-  Metadata

   -  BIDS metadata now uniformly refers to subjects and participants
      using the metadata key ‘subject’

Enhancements and new features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Extractors now report progress (with DataLad 0.10+)
-  BIDS participant metadata is now read via pybids

Fixes
~~~~~

-  Fix issue with unicode characters in BIDS metadata
-  DICOM metadata now also contains the ‘PatientName’ field that was
   previously excluded due to a too restrictive data type filter
