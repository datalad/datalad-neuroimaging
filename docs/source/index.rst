DataLad extension module for neuroimaging
*****************************************

.. toctree::
   :maxdepth: 1

   changelog
   acknowledgements

Demos
=====

.. toctree::
   :maxdepth: 2

   usecases/index

API
===

High-level API commands
-----------------------

.. currentmodule:: datalad.api
.. autosummary::
   :toctree: generated

   bids2scidata


Command line reference
----------------------

.. toctree::
   :maxdepth: 1

   generated/man/datalad-bids2scidata.rst


Metadata
========

This extension adds metadata extraction support for a range of standards common to
neuroimaging data.

Brain Imaging Data Structure (``bids``)
---------------------------------------

This extractor has basic support for the `BIDS <http://bids.neuroimaging.io>`_
standard.  This includes participant information, as well as acquisition
properties for individual files.  At present, there is no standardized
vocabulary for BIDS, instead field names are based on the conventions in the
standard description.


Digital Imaging and Communications in Medicine (``dicom``)
----------------------------------------------------------

Metadata can be extracted from any standard DICOM file. The extractor yields
file-based metadata, and a dataset-level description that identifies individual
image series. For each image series, all metadata are reported that are
invariant across individual images in a series. The extractor uses an
incomplete DICOM vocabulary from http://semantic-dicom.org


Neuroimaging data exchange format (``nifti1``)
----------------------------------------------

NIfTI-1 metadata is extracted from the header of individual files. Virtually
all header information is reported, except for header extensions.  An
adhoc-vocabulary is used, as no standard vocabulary is available.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. |---| unicode:: U+02014 .. em dash
