# emacs: -*- mode: python-mode; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Test NIDM results extractor"""

from shutil import copy
from shutil import make_archive
import os.path as op
from datalad.api import Dataset
from datalad.tests.utils import with_tree
from datalad.tests.utils import with_tempfile
from datalad.tests.utils import ok_clean_git
from datalad.tests.utils import assert_status
from datalad.tests.utils import assert_in
from datalad.tests.utils import assert_result_count


example_metadata = """\
{
  "@context": {
    "FeasibleGeneralizedLeastSquaresEstimation": "http://purl.obolibrary.org/obo/STATO_0000374",
    "termEditor": "http://purl.obolibrary.org/obo/IAO_0000117",
    "targetIntensity": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000124",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "owl": "http://www.w3.org/2002/07/owl#",
    "nlx": "http://uri.neuinfo.org/nif/nifstd/",
    "OrganizationalTerm": "http://purl.obolibrary.org/obo/IAO_0000121",
    "IndependentParameter": "http://purl.org/nidash/nidm#NIDM_0000073",
    "ContinuousProbabilityDistribution": "http://purl.obolibrary.org/obo/STATO_0000067",
    "CompoundSymmetryCovarianceStructure": "http://purl.obolibrary.org/obo/STATO_0000362",
    "noiseRoughnessInVoxels": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000145",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "PendingFinalVetting": "http://purl.obolibrary.org/obo/IAO_0000125",
    "ZStatistic": "http://purl.obolibrary.org/obo/STATO_0000376",
    "GeneralizedLeastSquaresEstimation": "http://purl.obolibrary.org/obo/STATO_0000372",
    "searchVolumeInVoxels": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000121",
      "@type": "http://www.w3.org/2001/XMLSchema#int"
    },
    "scr": "http://scicrunch.org/resolver/",
    "hasShortcutProperty": {
      "@id": "http://purl.org/ontology/prv/core#shortcut_property",
      "@type": "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property"
    },
    "title": "http://purl.org/dc/elements/1.1/title",
    "clusterSizeInVertices": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000083",
      "@type": "http://www.w3.org/2001/XMLSchema#int"
    },
    "isUserDefined": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000106",
      "@type": "http://www.w3.org/2001/XMLSchema#boolean"
    },
    "HeightThreshold": "http://purl.org/nidash/nidm#NIDM_0000034",
    "ExtentThreshold": "http://purl.org/nidash/nidm#NIDM_0000026",
    "CoordinateSpace": "http://purl.org/nidash/nidm#NIDM_0000016",
    "UnstructuredCovarianceStructure": "http://purl.obolibrary.org/obo/STATO_0000405",
    "FSLsGammaHRF": "http://purl.org/nidash/fsl#FSL_0000006",
    "SPM": "http://scicrunch.org/resolver/SCR_007037",
    "DisplayMaskMap": "http://purl.org/nidash/nidm#NIDM_0000020",
    "ResidualMeanSquaresMap": "http://purl.org/nidash/nidm#NIDM_0000066",
    "ContrastEstimation": "http://purl.org/nidash/nidm#NIDM_0000001",
    "minDistanceBetweenPeaks": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000109",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "smallestSignificantClusterSizeInVerticesFDR05": {
      "@id": "http://purl.org/nidash/spm#SPM_0000011",
      "@type": "http://www.w3.org/2001/XMLSchema#int"
    },
    "MNICoordinateSystem": "http://purl.org/nidash/nidm#NIDM_0000051",
    "ContrastExplainedMeanSquareMap": "http://purl.org/nidash/nidm#NIDM_0000163",
    "DiscreteProbabilityDistribution": "http://purl.obolibrary.org/obo/STATO_0000117",
    "IcbmMni152NonLinear2009cAsymmetricCoordinateSystem": "http://purl.org/nidash/nidm#NIDM_0000045",
    "ErrorDistribution": "http://purl.org/nidash/nidm#NIDM_0000022",
    "GaussianDistribution": "http://purl.org/nidash/nidm#NIDM_0000032",
    "Positron emission tomography scanner": "http://uri.neuinfo.org/nif/nifstd/ixl_0050000",
    "SPMsTemporalDerivative": "http://purl.org/nidash/spm#SPM_0000006",
    "Imaging instrument": "http://uri.neuinfo.org/nif/nifstd/birnlex_2094",
    "dc": "http://purl.org/dc/elements/1.1/",
    "NIDMResults": "http://purl.org/nidash/nidm#NIDM_0000027",
    "TalairachCoordinateSystem": "http://purl.org/nidash/nidm#NIDM_0000078",
    "records": {
      "@id": "@graph",
      "@container": "@type"
    },
    "Cluster": "http://purl.org/nidash/nidm#NIDM_0000006",
    "PositronEmissionTomographyScanner": "http://uri.neuinfo.org/nif/nifstd/ixl_0050000",
    "dimensionsInVoxels": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000090",
      "@type": "http://www.w3.org/2001/XMLSchema#string"
    },
    "OrdinaryLeastSquaresEstimation": "http://purl.obolibrary.org/obo/STATO_0000370",
    "numberOfDimensions": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000112",
      "@type": "http://www.w3.org/2001/XMLSchema#int"
    },
    "effectDegreesOfFreedom": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000091",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "NonParametricDistribution": "http://purl.org/nidash/nidm#NIDM_0000058",
    "smallestSignificantClusterSizeInVoxelsFWE05": {
      "@id": "http://purl.org/nidash/spm#SPM_0000014",
      "@type": "http://www.w3.org/2001/XMLSchema#int"
    },
    "ContrastMap": "http://purl.org/nidash/nidm#NIDM_0000002",
    "GaussianRunningLineDriftModel": "http://purl.org/nidash/fsl#FSL_0000002",
    "alternativeTerm": "http://purl.obolibrary.org/obo/IAO_0000118",
    "CustomCoordinateSystem": "http://purl.org/nidash/nidm#NIDM_0000017",
    "TStatistic": "http://purl.obolibrary.org/obo/STATO_0000176",
    "NIDMResultsExporter": "http://purl.org/nidash/nidm#NIDM_0000165",
    "hasDriftModel": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000088",
      "@type": "http://purl.org/nidash/spm#SPM_0000002"
    },
    "Icbm452AirCoordinateSystem": "http://purl.org/nidash/nidm#NIDM_0000038",
    "nfo": "http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#",
    "coordinateVector": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000086",
      "@type": "http://www.w3.org/2001/XMLSchema#string"
    },
    "statisticType": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000123",
      "@type": "http://purl.obolibrary.org/obo/STATO_0000176"
    },
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "Statistic": "http://purl.obolibrary.org/obo/STATO_0000039",
    "ConstantParameter": "http://purl.org/nidash/nidm#NIDM_0000072",
    "IAORelease20150223": "http://purl.obolibrary.org/obo/iao/2015-02-23/iao.owl",
    "FSLsGammaDifferenceHRF": "http://purl.org/nidash/fsl#FSL_0000001",
    "RegularizedParameter": "http://purl.org/nidash/nidm#NIDM_0000074",
    "IcbmMni152NonLinear2009aSymmetricCoordinateSystem": "http://purl.org/nidash/nidm#NIDM_0000042",
    "SineBasisSet": "http://purl.org/nidash/nidm#NIDM_0000151",
    "HemodynamicResponseFunctionDerivative": "http://purl.org/nidash/nidm#NIDM_0000037",
    "BFOCLIFSpecificationLabel": "http://purl.obolibrary.org/obo/BFO_0000180",
    "exampleOfUsage": "http://purl.obolibrary.org/obo/IAO_0000112",
    "GammaHRF": "http://purl.org/nidash/nidm#NIDM_0000031",
    "creator": "http://purl.org/dc/elements/1.1/creator",
    "DiffusionWeightedImagingProtocol": "http://uri.neuinfo.org/nif/nifstd/nlx_inv_20090249",
    "FourierBasisSet": "http://purl.org/nidash/nidm#NIDM_0000069",
    "ArbitrarilyCorrelatedError": "http://purl.org/nidash/nidm#NIDM_0000003",
    "voxelUnits": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000133",
      "@type": "http://www.w3.org/2001/XMLSchema#string"
    },
    "DiscreteCosineTransformbasisDriftModel": "http://purl.org/nidash/spm#SPM_0000002",
    "noiseFWHMInVoxels": "http://purl.org/nidash/spm#SPM_0000009",
    "crypto": "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#",
    "LegendrePolynomialOrder": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000014",
      "@type": "http://www.w3.org/2001/XMLSchema#int"
    },
    "errorDegreesOfFreedom": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000093",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "searchVolumeInResels": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000149",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "StudyGroupPopulation": "http://purl.obolibrary.org/obo/STATO_0000193",
    "definitionSource": "http://purl.obolibrary.org/obo/IAO_0000119",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "description": {
      "@id": "http://purl.org/dc/elements/1.1/description",
      "@type": "http://purl.org/dc/dcmitype/Image"
    },
    "voxel6connected": "http://purl.org/nidash/nidm#NIDM_0000130",
    "SubjectCoordinateSystem": "http://purl.org/nidash/nidm#NIDM_0000077",
    "userSpecifiedThresholdType": "http://purl.org/nidash/nidm#NIDM_0000125",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "NonParametricSymmetricDistribution": "http://purl.org/nidash/nidm#NIDM_0000059",
    "hasMapHeader": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000103",
      "@type": "http://purl.org/nidash/nidm#NIDM_0000053"
    },
    "randomFieldStationarity": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000120",
      "@type": "http://www.w3.org/2001/XMLSchema#boolean"
    },
    "expectedNumberOfVerticesPerCluster": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000142",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "ParameterEstimateMap": "http://purl.org/nidash/nidm#NIDM_0000061",
    "GammaBasisSet": "http://purl.org/nidash/nidm#NIDM_0000030",
    "BFOOWLSpecificationLabel": "http://purl.obolibrary.org/obo/BFO_0000179",
    "IcbmMni152NonLinear2009aAsymmetricCoordinateSystem": "http://purl.org/nidash/nidm#NIDM_0000041",
    "version": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000127",
      "@type": "http://www.w3.org/2001/XMLSchema#string"
    },
    "RequiresDiscussion": "http://purl.obolibrary.org/obo/IAO_0000428",
    "varianceMapWiseDependence": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000126",
      "@type": "http://purl.org/nidash/nidm#NIDM_0000074"
    },
    "contrastName": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000085",
      "@type": "http://www.w3.org/2001/XMLSchema#string"
    },
    "editorPreferredTerm": "http://purl.obolibrary.org/obo/IAO_0000111",
    "ReselsPerVoxelMap": "http://purl.org/nidash/nidm#NIDM_0000144",
    "SPMsDispersionDerivative": "http://purl.org/nidash/spm#SPM_0000003",
    "ModelParameterEstimation": "http://purl.org/nidash/nidm#NIDM_0000056",
    "ToeplitzCovarianceStructure": "http://purl.obolibrary.org/obo/STATO_0000357",
    "GrandMeanMap": "http://purl.org/nidash/nidm#NIDM_0000033",
    "hasErrorDistribution": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000101",
      "@type": "http://purl.obolibrary.org/obo/STATO_0000067"
    },
    "GammaDifferenceHRF": "http://purl.org/nidash/nidm#NIDM_0000029",
    "withEstimationMethod": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000134",
      "@type": "http://purl.obolibrary.org/obo/STATO_0000119"
    },
    "PixelConnectivityCriterion": "http://purl.org/nidash/nidm#NIDM_0000064",
    "nidm": "http://purl.org/nidash/nidm#",
    "clusterSizeInVoxels": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000084",
      "@type": "http://www.w3.org/2001/XMLSchema#int"
    },
    "hasShortcut": {
      "@id": "http://purl.org/ontology/prv/core#shortcut",
      "@type": "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property"
    },
    "WeightedLeastSquaresEstimation": "http://purl.obolibrary.org/obo/STATO_0000371",
    "dct": "http://purl.org/dc/terms/",
    "ConnectivityCriterion": "http://purl.org/nidash/nidm#NIDM_0000012",
    "StructuralMRIProtocol": "http://uri.neuinfo.org/nif/nifstd/birnlex_2251",
    "niiri": "http://iri.nidash.org/",
    "reselSizeInVoxels": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000148",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "hasMRIProtocol": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000172",
      "@type": "http://uri.neuinfo.org/nif/nifstd/nlx_inv_20090249"
    },
    "definition": "http://purl.obolibrary.org/obo/IAO_0000115",
    "DriftModel": "http://purl.org/nidash/nidm#NIDM_0000087",
    "Magnetoencephalography machine": "http://uri.neuinfo.org/nif/nifstd/ixl_0050002",
    "IcbmMni152NonLinear2009cSymmetricCoordinateSystem": "http://purl.org/nidash/nidm#NIDM_0000046",
    "voxel18connected": "http://purl.org/nidash/nidm#NIDM_0000128",
    "voxel26connected": "http://purl.org/nidash/nidm#NIDM_0000129",
    "hasMaximumIntensityProjection": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000138",
      "@type": "http://purl.org/dc/dcmitype/Image"
    },
    "NormalDistribution": "http://purl.obolibrary.org/obo/STATO_0000227",
    "hasConnectivityCriterion": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000099",
      "@type": "http://purl.org/nidash/nidm#NIDM_0000064"
    },
    "ClusterLabelsMap": "http://purl.org/nidash/nidm#NIDM_0000008",
    "ChiSquaredStatistic": "http://purl.obolibrary.org/obo/STATO_0000030",
    "Mni305CoordinateSystem": "http://purl.org/nidash/nidm#NIDM_0000055",
    "importedFrom": "http://purl.obolibrary.org/obo/IAO_0000412",
    "BinomialDistribution": "http://purl.org/nidash/nidm#NIDM_0000005",
    "ClusterDefinitionCriteria": "http://purl.org/nidash/nidm#NIDM_0000007",
    "@version": 1.1,
    "CustomBasisSet": "http://purl.org/nidash/nidm#NIDM_0000067",
    "ReadyForRelease": "http://purl.obolibrary.org/obo/IAO_0000122",
    "hasAlternativeHypothesis": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000097",
      "@type": "http://purl.org/nidash/nidm#NIDM_0000060"
    },
    "pValueFWER": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000115",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "PeakDefinitionCriteria": "http://purl.org/nidash/nidm#NIDM_0000063",
    "pixel4connected": "http://purl.org/nidash/nidm#NIDM_0000117",
    "AFNIsGammaHRF": "http://purl.org/nidash/afni#GammaHRF",
    "ConjunctionInference": "http://purl.org/nidash/nidm#NIDM_0000011",
    "IcbmMni152LinearCoordinateSystem": "http://purl.org/nidash/nidm#NIDM_0000040",
    "FSL": "http://scicrunch.org/resolver/SCR_002823",
    "MaskMap": "http://purl.org/nidash/nidm#NIDM_0000054",
    "CovarianceStructure": "http://purl.obolibrary.org/obo/STATO_0000346",
    "contributor": "http://purl.org/dc/elements/1.1/contributor",
    "heightCriticalThresholdFDR05": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000146",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "AFNIsLegendrePolinomialDriftModel": "http://purl.org/nidash/afni#LegendrePolynomialDriftModel",
    "numberOfSubjects": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000171",
      "@type": "http://www.w3.org/2001/XMLSchema#int"
    },
    "IcbmMni152NonLinear2009bAsymmetricCoordinateSystem": "http://purl.org/nidash/nidm#NIDM_0000043",
    "hasClusterLabelsMap": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000098",
      "@type": "http://purl.org/nidash/nidm#NIDM_0000008"
    },
    "expectedNumberOfClusters": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000141",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "Structural MRI protocol": "http://uri.neuinfo.org/nif/nifstd/birnlex_2251",
    "ExcursionSetMap": "http://purl.org/nidash/nidm#NIDM_0000025",
    "VoxelConnectivityCriterion": "http://purl.org/nidash/nidm#NIDM_0000080",
    "numberOfSupraThresholdClusters": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000111",
      "@type": "http://www.w3.org/2001/XMLSchema#int"
    },
    "ToBeReplacedWithExternalOntologyTerm": "http://purl.obolibrary.org/obo/IAO_0000423",
    "FSLsTemporalDerivative": "http://purl.org/nidash/fsl#FSL_0000003",
    "pValue": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000114",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "FWERAdjustedPValue": "http://purl.obolibrary.org/obo/OBI_0001265",
    "ExchangeableError": "http://purl.org/nidash/nidm#NIDM_0000024",
    "MapHeader": "http://purl.org/nidash/nidm#NIDM_0000053",
    "MetadataIncomplete": "http://purl.obolibrary.org/obo/IAO_0000123",
    "MetadataComplete": "http://purl.obolibrary.org/obo/IAO_0000120",
    "qValueFDR": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000119",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "IndependentError": "http://purl.org/nidash/nidm#NIDM_0000048",
    "hasHRFBasis": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000102",
      "@type": "http://purl.org/nidash/nidm#NIDM_0000028"
    },
    "ErrorModel": "http://purl.org/nidash/nidm#NIDM_0000023",
    "ImagingInstrument": "http://uri.neuinfo.org/nif/nifstd/birnlex_2094",
    "inCoordinateSpace": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000104",
      "@type": "http://purl.org/nidash/nidm#NIDM_0000016"
    },
    "Peak": "http://purl.org/nidash/nidm#NIDM_0000062",
    "DataScaling": "http://purl.org/nidash/nidm#NIDM_0000018",
    "BinaryMap": "http://purl.org/nidash/nidm#NIDM_0000004",
    "ConvolutionBasisSet": "http://purl.org/nidash/nidm#NIDM_0000036",
    "pValueUncorrected": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000116",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "obo": "http://purl.obolibrary.org/obo/",
    "OneTailedTest": "http://purl.org/nidash/nidm#NIDM_0000060",
    "afni": "http://purl.org/nidash/afni#",
    "GaussianHRF": "http://purl.org/nidash/nidm#NIDM_0000110",
    "QValue": "http://purl.obolibrary.org/obo/OBI_0001442",
    "clusterLabelId": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000082",
      "@type": "http://www.w3.org/2001/XMLSchema#int"
    },
    "Coordinate": "http://purl.org/nidash/nidm#NIDM_0000015",
    "Electroencephalography machine": "http://uri.neuinfo.org/nif/nifstd/ixl_0050003",
    "PropertyReification": "http://purl.org/ontology/prv/core#PropertyReification",
    "voxelSize": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000131",
      "@type": "http://www.w3.org/2001/XMLSchema#string"
    },
    "IcbmMni152NonLinear2009bSymmetricCoordinateSystem": "http://purl.org/nidash/nidm#NIDM_0000044",
    "expectedNumberOfVoxelsPerCluster": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000143",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "LinearSplineBasisSet": "http://purl.org/nidash/nidm#NIDM_0000150",
    "Data": "http://purl.org/nidash/nidm#NIDM_0000169",
    "MagnetoencephalographyMachine": "http://uri.neuinfo.org/nif/nifstd/ixl_0050002",
    "grandMeanScaling": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000096",
      "@type": "http://www.w3.org/2001/XMLSchema#boolean"
    },
    "Single-photon emission computed tomography scanner": "http://uri.neuinfo.org/nif/nifstd/ixl_0050001",
    "clusterSizeInResels": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000156",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "ContrastStandardErrorMap": "http://purl.org/nidash/nidm#NIDM_0000013",
    "softwareVersion": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000122",
      "@type": "http://www.w3.org/2001/XMLSchema#string"
    },
    "Uncurated": "http://purl.obolibrary.org/obo/IAO_0000124",
    "inWorldCoordinateSystem": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000105",
      "@type": "http://purl.org/nidash/nidm#NIDM_0000017"
    },
    "regressorNames": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000021",
      "@type": "http://www.w3.org/2001/XMLSchema#string"
    },
    "NIDMResultsExport": "http://purl.org/nidash/nidm#NIDM_0000166",
    "Diffusion-weighted imaging protocol": "http://uri.neuinfo.org/nif/nifstd/nlx_inv_20090249",
    "IterativelyReweightedLeastSquaresEstimation": "http://purl.obolibrary.org/obo/STATO_0000373",
    "noiseFWHMInVertices": "http://purl.org/nidash/spm#SPM_0000008",
    "elucidation": "http://purl.obolibrary.org/obo/IAO_0000600",
    "maskedMedian": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000107",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "errorVarianceHomogeneous": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000094",
      "@type": "http://www.w3.org/2001/XMLSchema#boolean"
    },
    "objectModel": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000113",
      "@type": "http://purl.org/nidash/nidm#NIDM_0000057"
    },
    "searchVolumeInVertices": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000137",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "noiseFWHMInUnits": "http://purl.org/nidash/spm#SPM_0000007",
    "IcbmMni152NonLinear6thGenerationCoordinateSystem": "http://purl.org/nidash/nidm#NIDM_0000047",
    "hasErrorDependence": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000100",
      "@type": "http://purl.obolibrary.org/obo/STATO_0000405"
    },
    "searchVolumeReselsGeometry": {
      "@id": "http://purl.org/nidash/spm#SPM_0000010",
      "@type": "http://www.w3.org/2001/XMLSchema#string"
    },
    "hasCurationStatus": "http://purl.obolibrary.org/obo/IAO_0000114",
    "smallestSignificantClusterSizeInVoxelsFDR05": {
      "@id": "http://purl.org/nidash/spm#SPM_0000013",
      "@type": "http://www.w3.org/2001/XMLSchema#int"
    },
    "Magnetic resonance imaging scanner": "http://uri.neuinfo.org/nif/nifstd/birnlex_2100",
    "spm": "http://purl.org/nidash/nidm#NIDM_0000168",
    "TwoTailedTest": "http://purl.org/nidash/nidm#NIDM_0000079",
    "SPMsCanonicalHRF": "http://purl.org/nidash/spm#SPM_0000004",
    "Functional MRI protocol": "http://uri.neuinfo.org/nif/nifstd/birnlex_2250",
    "NIDMObjectModel": "http://purl.org/nidash/nidm#NIDM_0000057",
    "Icbm452Warp5CoordinateSystem": "http://purl.org/nidash/nidm#NIDM_0000039",
    "ProbabilityDistribution": "http://purl.obolibrary.org/obo/STATO_0000225",
    "coordinateVectorInVoxels": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000139",
      "@type": "http://www.w3.org/2001/XMLSchema#string"
    },
    "ElectroencephalographyMachine": "http://uri.neuinfo.org/nif/nifstd/ixl_0050003",
    "SupraThresholdCluster": "http://purl.org/nidash/nidm#NIDM_0000070",
    "StandardizedCoordinateSystem": "http://purl.org/nidash/nidm#NIDM_0000075",
    "Map": "http://purl.org/nidash/nidm#NIDM_0000052",
    "pixel8connected": "http://purl.org/nidash/nidm#NIDM_0000118",
    "PValueUncorrected": "http://purl.org/nidash/nidm#NIDM_0000160",
    "dependenceMapWiseDependence": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000089",
      "@type": "http://purl.org/nidash/nidm#NIDM_0000074"
    },
    "driftCutoffPeriod": {
      "@id": "http://purl.org/nidash/fsl#FSL_0000004",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "hasObjectProperty": {
      "@id": "http://purl.org/ontology/prv/core#object_property",
      "@type": "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property"
    },
    "DesignMatrix": "http://purl.org/nidash/nidm#NIDM_0000019",
    "equivalentThreshold": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000161",
      "@type": "http://purl.org/nidash/nidm#NIDM_0000162"
    },
    "editorNote": "http://purl.obolibrary.org/obo/IAO_0000116",
    "FunctionalMRIProtocol": "http://uri.neuinfo.org/nif/nifstd/birnlex_2250",
    "curatorNote": "http://purl.obolibrary.org/obo/IAO_0000232",
    "ClusterCenterOfGravity": "http://purl.org/nidash/nidm#NIDM_0000140",
    "ExampleToBeEventuallyRemoved": "http://purl.obolibrary.org/obo/IAO_0000002",
    "nidmfsl": "http://purl.org/nidash/nidm#NIDM_0000167",
    "groupName": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000170",
      "@type": "http://www.w3.org/2001/XMLSchema#string"
    },
    "ErrorParameterMapWiseDependence": "http://purl.org/nidash/nidm#NIDM_0000071",
    "SearchSpaceMaskMap": "http://purl.org/nidash/nidm#NIDM_0000068",
    "SPMsDriftCutoffPeriod": {
      "@id": "http://purl.org/nidash/spm#SPM_0000001",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "Colin27CoordinateSystem": "http://purl.org/nidash/nidm#NIDM_0000009",
    "partialConjunctionDegree": {
      "@id": "http://purl.org/nidash/spm#SPM_0000015",
      "@type": "http://www.w3.org/2001/XMLSchema#int"
    },
    "featVersion": {
      "@id": "http://purl.org/nidash/fsl#FSL_0000005",
      "@type": "http://www.w3.org/2001/XMLSchema#string"
    },
    "IsAbout": "http://purl.obolibrary.org/obo/IAO_0000136",
    "ContrastWeightMatrix": "http://purl.obolibrary.org/obo/STATO_0000323",
    "HasValue": "http://purl.obolibrary.org/obo/STATO_0000129",
    "MRIProtocol": "http://uri.neuinfo.org/nif/nifstd/birnlex_2177",
    "heightCriticalThresholdFWE05": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000147",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "hasReificationClass": {
      "@id": "http://purl.org/ontology/prv/core#reification_class",
      "@type": "http://www.w3.org/2002/07/owl#Class"
    },
    "equivalentZStatistic": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000092",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "smallestSignificantClusterSizeInVerticesFWE05": {
      "@id": "http://purl.org/nidash/spm#SPM_0000012",
      "@type": "http://www.w3.org/2001/XMLSchema#int"
    },
    "MRI protocol": "http://uri.neuinfo.org/nif/nifstd/birnlex_2177",
    "date": "http://purl.org/dc/elements/1.1/date",
    "maxNumberOfPeaksPerCluster": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000108",
      "@type": "http://www.w3.org/2001/XMLSchema#int"
    },
    "PoissonDistribution": "http://purl.org/nidash/nidm#NIDM_0000065",
    "WorldCoordinateSystem": "http://purl.org/nidash/nidm#NIDM_0000081",
    "Ixi549CoordinateSystem": "http://purl.org/nidash/nidm#NIDM_0000050",
    "Inference": "http://purl.org/nidash/nidm#NIDM_0000049",
    "FStatistic": "http://purl.obolibrary.org/obo/STATO_0000282",
    "hasSubjectProperty": {
      "@id": "http://purl.org/ontology/prv/core#subject_property",
      "@type": "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property"
    },
    "NeuroimagingAnalysisSoftware": "http://purl.org/nidash/nidm#NIDM_0000164",
    "AnatomicalMRIProtocol": "http://uri.neuinfo.org/nif/nifstd/ixl_0050004",
    "fsl": "http://purl.org/nidash/fsl#",
    "PartialConjunctionInference": "http://purl.org/nidash/spm#SPM_0000005",
    "FiniteImpulseResponseBasisSet": "http://purl.org/nidash/nidm#NIDM_0000028",
    "ContrastVarianceMap": "http://purl.org/nidash/nidm#NIDM_0000135",
    "SinglePhotonEmissionComputedTomographyScanner": "http://uri.neuinfo.org/nif/nifstd/ixl_0050001",
    "MagneticResonanceImagingScanner": "http://uri.neuinfo.org/nif/nifstd/birnlex_2100",
    "HemodynamicResponseFunction": "http://purl.org/nidash/nidm#NIDM_0000035",
    "prov": "http://www.w3.org/ns/prov#",
    "Threshold": "http://purl.org/nidash/nidm#NIDM_0000162",
    "searchVolumeInUnits": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000136",
      "@type": "http://www.w3.org/2001/XMLSchema#float"
    },
    "StatisticMap": "http://purl.org/nidash/nidm#NIDM_0000076",
    "voxelToWorldMapping": {
      "@id": "http://purl.org/nidash/nidm#NIDM_0000132",
      "@type": "http://www.w3.org/2001/XMLSchema#string"
    }
  },
  "@id": "file:///Users/camaumet/Softs/nidm-specs/nidm/nidm-results/spm/spm_results.ttl",
  "records": {
    "PeakDefinitionCriteria": {
      "maxNumberOfPeaksPerCluster": "3",
      "minDistanceBetweenPeaks": "8.0",
      "@id": "niiri:peak_definition_criteria_id",
      "rdfs:label": "Peak Definition Criteria"
    },
    "DesignMatrix": {
      "rdfs:label": "Design Matrix",
      "dc:description": {
        "@id": "niiri:design_matrix_png_id"
      },
      "nfo:fileName": "DesignMatrix.csv",
      "prov:atLocation": {
        "@type": "xsd:anyURI",
        "@value": "DesignMatrix.csv"
      },
      "@id": "niiri:design_matrix_id",
      "dct:format": "text/csv"
    },
    "HeightThreshold": [
      {
        "nidm:NIDM_0000161": [
          {
            "@id": "niiri:height_threshold_id_2"
          },
          {
            "@id": "niiri:height_threshold_id_3"
          }
        ],
        "@id": "niiri:height_threshold_id",
        "@type": "FWERAdjustedPValue",
        "prov:value": {
          "@type": "xsd:float",
          "@value": "0.05"
        },
        "rdfs:label": "Height Threshold: p<0.05 (FWE)"
      },
      {
        "rdfs:label": "Height Threshold: p<5.23529984739211",
        "@id": "niiri:height_threshold_id_2",
        "@type": "Statistic",
        "prov:value": {
          "@type": "xsd:float",
          "@value": "5.23529984739"
        }
      }
    ],
    "StudyGroupPopulation": [
      {
        "rdfs:label": "Group: Patient",
        "@id": "niiri:group2_id",
        "nidm:NIDM_0000170": "Patient",
        "numberOfSubjects": "21"
      },
      {
        "rdfs:label": "Group: Control",
        "@id": "niiri:group_id",
        "nidm:NIDM_0000170": "Control",
        "numberOfSubjects": "23"
      }
    ],
    "ParameterEstimateMap": [
      {
        "prov:wasDerivedFrom": {
          "@id": "niiri:beta_map_id_2_der"
        },
        "rdfs:label": "Beta Map 2",
        "prov:wasGeneratedBy": {
          "@id": "niiri:model_pe_id"
        },
        "nfo:fileName": "ParameterEstimate_002.nii.gz",
        "nidm:NIDM_0000104": {
          "@id": "niiri:coordinate_space_id_1"
        },
        "prov:atLocation": {
          "@type": "xsd:anyURI",
          "@value": "ParameterEstimate_002.nii"
        },
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
        "@id": "niiri:beta_map_id_2",
        "dct:format": "image/nifti"
      },
      {
        "prov:wasDerivedFrom": {
          "@id": "niiri:beta_map_id_1_der"
        },
        "rdfs:label": "Beta Map 1",
        "prov:wasGeneratedBy": {
          "@id": "niiri:model_pe_id"
        },
        "nfo:fileName": "ParameterEstimate_001.nii.gz",
        "nidm:NIDM_0000104": {
          "@id": "niiri:coordinate_space_id_1"
        },
        "prov:atLocation": {
          "@type": "xsd:anyURI",
          "@value": "ParameterEstimate_001.nii.gz"
        },
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
        "@id": "niiri:beta_map_id_1",
        "dct:format": "image/nifti"
      },
      {
        "nfo:fileName": "beta_0002.img",
        "nidm:NIDM_0000103": {
          "@id": "niiri:original_pe_map_header_2_id"
        },
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
        "@id": "niiri:beta_map_id_2_der",
        "dct:format": "image/nifti"
      },
      {
        "nfo:fileName": "beta_0001.img",
        "nidm:NIDM_0000103": {
          "@id": "niiri:original_pe_map_header_id"
        },
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
        "@id": "niiri:beta_map_id_1_der",
        "dct:format": "image/nifti"
      }
    ],
    "GrandMeanMap": {
      "rdfs:label": "Grand Mean Map",
      "prov:wasGeneratedBy": {
        "@id": "niiri:model_pe_id"
      },
      "maskedMedian": "115.0",
      "nfo:fileName": "GrandMean.nii.gz",
      "nidm:NIDM_0000104": {
        "@id": "niiri:coordinate_space_id_1"
      },
      "prov:atLocation": {
        "@type": "xsd:anyURI",
        "@value": "GrandMean.nii.gz"
      },
      "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
      "@id": "niiri:grand_mean_map_id",
      "dct:format": "image/nifti"
    },
    "prov:SoftwareAgent": {
      "rdfs:label": "SPM",
      "nidm:NIDM_0000122": "12b.5853",
      "@id": "niiri:software_id",
      "@type": "SPM"
    },
    "PValueUncorrected": [
      {
        "rdfs:label": "Extent Threshold",
        "@id": "niiri:extent_threshold_id_3",
        "@type": "ExtentThreshold",
        "prov:value": {
          "@type": "xsd:float",
          "@value": "1.0"
        }
      },
      {
        "rdfs:label": "Height Threshold: p<7.62276079258051e-07 (uncorrected)",
        "@id": "niiri:height_threshold_id_3",
        "@type": "HeightThreshold",
        "prov:value": {
          "@type": "xsd:float",
          "@value": "7.62276079258e-07"
        }
      }
    ],
    "SupraThresholdCluster": [
      {
        "prov:wasDerivedFrom": {
          "@id": "niiri:excursion_set_map_id"
        },
        "pValueFWER": "1.392379545e-10",
        "clusterSizeInVoxels": "38",
        "pValueUncorrected": "1.56592642027e-09",
        "rdfs:label": "Supra-Threshold Cluster 0003",
        "qValueFDR": "4.17580378739e-09",
        "clusterSizeInResels": "1.65772626435",
        "clusterLabelId": "3",
        "@id": "niiri:supra_threshold_cluster_0003"
      },
      {
        "prov:wasDerivedFrom": {
          "@id": "niiri:excursion_set_map_id"
        },
        "pValueFWER": "0.0",
        "clusterSizeInVoxels": "445",
        "pValueUncorrected": "3.91543427862e-46",
        "rdfs:label": "Supra-Threshold Cluster 0002",
        "qValueFDR": "1.56617371145e-45",
        "clusterSizeInResels": "19.412847043",
        "clusterLabelId": "2",
        "@id": "niiri:supra_threshold_cluster_0002"
      },
      {
        "prov:wasDerivedFrom": {
          "@id": "niiri:excursion_set_map_id"
        },
        "pValueFWER": "0.0",
        "clusterSizeInVoxels": "530",
        "pValueUncorrected": "9.56276736481e-52",
        "rdfs:label": "Supra-Threshold Cluster 0001",
        "qValueFDR": "7.65021389185e-51",
        "clusterSizeInResels": "23.1209189501",
        "clusterLabelId": "1",
        "@id": "niiri:supra_threshold_cluster_0001"
      }
    ],
    "MaskMap": [
      {
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
        "nfo:fileName": "MaskMap_1_der.nii",
        "@id": "niiri:mask_id_1_der",
        "dct:format": "image/nifti"
      },
      {
        "nfo:fileName": "mask.img",
        "nidm:NIDM_0000103": {
          "@id": "niiri:original_mask_map_header_id"
        },
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
        "@id": "niiri:mask_id_2_der",
        "dct:format": "image/nifti"
      },
      {
        "prov:wasDerivedFrom": {
          "@id": "niiri:mask_id_1_der"
        },
        "rdfs:label": "Mask Map 1",
        "nfo:fileName": "Mask_1.nii.gz",
        "nidm:NIDM_0000106": true,
        "nidm:NIDM_0000104": {
          "@id": "niiri:coordinate_space_id_1"
        },
        "prov:atLocation": {
          "@type": "xsd:anyURI",
          "@value": "Mask_1.nii.gz"
        },
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
        "@id": "niiri:mask_id_1",
        "dct:format": "image/nifti"
      },
      {
        "prov:wasDerivedFrom": {
          "@id": "niiri:mask_id_2_der"
        },
        "rdfs:label": "Mask Map 2",
        "prov:wasGeneratedBy": {
          "@id": "niiri:model_pe_id"
        },
        "nfo:fileName": "Mask.nii.gz",
        "nidm:NIDM_0000106": false,
        "nidm:NIDM_0000104": {
          "@id": "niiri:coordinate_space_id_1"
        },
        "prov:atLocation": {
          "@type": "xsd:anyURI",
          "@value": "Mask.nii.gz"
        },
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
        "@id": "niiri:mask_id_2",
        "dct:format": "image/nifti"
      },
      {
        "rdfs:label": "Mask Map",
        "nfo:fileName": "Mask_3.nii.gz",
        "nidm:NIDM_0000106": true,
        "nidm:NIDM_0000104": {
          "@id": "niiri:coordinate_space_id_2"
        },
        "prov:atLocation": {
          "@type": "xsd:anyURI",
          "@value": "Mask_3.nii.gz"
        },
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
        "@id": "niiri:mask_id_3",
        "dct:format": "image/nifti"
      }
    ],
    "ExtentThreshold": [
      {
        "rdfs:label": "Extent Threshold: k>=0",
        "clusterSizeInVoxels": "0",
        "@id": "niiri:extent_threshold_id",
        "clusterSizeInResels": "0.0",
        "nidm:NIDM_0000161": [
          {
            "@id": "niiri:height_threshold_id_3"
          },
          {
            "@id": "niiri:height_threshold_id_2"
          }
        ],
        "@type": "Statistic"
      },
      {
        "rdfs:label": "Extent Threshold",
        "@id": "niiri:extent_threshold_id_2",
        "@type": "FWERAdjustedPValue",
        "prov:value": {
          "@type": "xsd:float",
          "@value": "1.0"
        }
      }
    ],
    "CoordinateSpace": [
      {
        "rdfs:label": "Coordinate space 2",
        "nidm:NIDM_0000132": "[[-3, 0, 0, 78],[0, 3, 0, -112],[0, 0, 3, -50],[0, 0, 0, 1]]",
        "nidm:NIDM_0000133": "[ \\"mm\\", \\"mm\\", \\"mm\\" ]",
        "nidm:NIDM_0000105": {
          "@id": "nidm:NIDM_0000051"
        },
        "nidm:NIDM_0000131": "[ 3, 3, 3 ]",
        "nidm:NIDM_0000090": "[ 53, 63, 46 ]",
        "numberOfDimensions": "3",
        "@id": "niiri:coordinate_space_id_2"
      },
      {
        "rdfs:label": "Coordinate space 1",
        "nidm:NIDM_0000132": "[[-3, 0, 0, 78],[0, 3, 0, -112],[0, 0, 3, -50],[0, 0, 0, 1]]",
        "nidm:NIDM_0000133": "[ \\"mm\\", \\"mm\\", \\"mm\\" ]",
        "nidm:NIDM_0000105": {
          "@id": "nidm:NIDM_0000051"
        },
        "nidm:NIDM_0000131": "[ 3, 3, 3 ]",
        "nidm:NIDM_0000090": "[ 53, 63, 46 ]",
        "numberOfDimensions": "3",
        "@id": "niiri:coordinate_space_id_1"
      }
    ],
    "prov:Generation": {
      "prov:atTime": {
        "@type": "xsd:dateTime",
        "@value": "2014-05-19T10:30:00+01:00"
      },
      "@id": "_:fbfe9825b225641a29fc0e8ac5eb8d33cb1",
      "prov:activity": {
        "@id": "niiri:export_id"
      }
    },
    "ExcursionSetMap": {
      "rdfs:label": "Excursion Set Map",
      "pValue": "8.95949980873e-14",
      "prov:wasGeneratedBy": {
        "@id": "niiri:inference_id"
      },
      "numberOfSupraThresholdClusters": "8",
      "nidm:NIDM_0000098": {
        "@id": "niiri:cluster_label_map_id"
      },
      "nfo:fileName": "ExcursionSet.nii.gz",
      "nidm:NIDM_0000104": {
        "@id": "niiri:coordinate_space_id_1"
      },
      "prov:atLocation": {
        "@type": "xsd:anyURI",
        "@value": "ExcursionSet.nii.gz"
      },
      "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
      "nidm:NIDM_0000138": {
        "@id": "niiri:maximum_intensity_projection_id"
      },
      "@id": "niiri:excursion_set_map_id",
      "dct:format": "image/nifti"
    },
    "MapHeader": [
      {
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a...",
        "nfo:fileName": "beta_0002.hdr",
        "@id": "niiri:original_pe_map_header_2_id",
        "@type": "prov:Entity",
        "dct:format": "image/nifti"
      },
      {
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a...",
        "nfo:fileName": "mask.hdr",
        "@id": "niiri:original_mask_map_header_id",
        "@type": "prov:Entity",
        "dct:format": "image/nifti"
      },
      {
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a...",
        "nfo:fileName": "con_0001.hdr",
        "@id": "niiri:original_contrast_map_header_id",
        "@type": "prov:Entity",
        "dct:format": "image/nifti"
      }
    ],
    "Peak": [
      {
        "prov:wasDerivedFrom": {
          "@id": "niiri:supra_threshold_cluster_0001"
        },
        "pValueFWER": "1.82057147136e-10",
        "equivalentZStatistic": "7.80404869241",
        "pValueUncorrected": "2.99760216649e-15",
        "rdfs:label": "Peak 0003",
        "qValueFDR": "9.95383070868e-08",
        "prov:value": {
          "@type": "xsd:float",
          "@value": "9.82185649872"
        },
        "prov:atLocation": {
          "@id": "niiri:coordinate_0003"
        },
        "@id": "niiri:peak_0003"
      },
      {
        "prov:wasDerivedFrom": {
          "@id": "niiri:supra_threshold_cluster_0001"
        },
        "pValueFWER": "0.0",
        "equivalentZStatistic": "inf",
        "pValueUncorrected": "4.4408920985e-16",
        "rdfs:label": "Peak 0002",
        "qValueFDR": "3.12855975726e-10",
        "prov:value": {
          "@type": "xsd:float",
          "@value": "11.345749855"
        },
        "prov:atLocation": {
          "@id": "niiri:coordinate_0002"
        },
        "@id": "niiri:peak_0002"
      },
      {
        "prov:wasDerivedFrom": {
          "@id": "niiri:supra_threshold_cluster_0002"
        },
        "pValueFWER": "0.0",
        "equivalentZStatistic": "inf",
        "pValueUncorrected": "4.4408920985e-16",
        "rdfs:label": "Peak 0005",
        "qValueFDR": "6.3705194445e-11",
        "prov:value": {
          "@type": "xsd:float",
          "@value": "12.3229017258"
        },
        "prov:atLocation": {
          "@id": "niiri:coordinate_0005"
        },
        "@id": "niiri:peak_0005"
      },
      {
        "prov:wasDerivedFrom": {
          "@id": "niiri:supra_threshold_cluster_0002"
        },
        "pValueFWER": "0.0",
        "equivalentZStatistic": "inf",
        "pValueUncorrected": "4.4408920985e-16",
        "rdfs:label": "Peak 0004",
        "qValueFDR": "6.3705194445e-11",
        "prov:value": {
          "@type": "xsd:float",
          "@value": "13.7208814621"
        },
        "prov:atLocation": {
          "@id": "niiri:coordinate_0004"
        },
        "@id": "niiri:peak_0004"
      },
      {
        "prov:wasDerivedFrom": {
          "@id": "niiri:supra_threshold_cluster_0002"
        },
        "pValueFWER": "4.22372581355e-10",
        "equivalentZStatistic": "7.70269435363",
        "pValueUncorrected": "6.66133814775e-15",
        "rdfs:label": "Peak 0006",
        "qValueFDR": "1.58195372182e-07",
        "prov:value": {
          "@type": "xsd:float",
          "@value": "9.62070846558"
        },
        "prov:atLocation": {
          "@id": "niiri:coordinate_0006"
        },
        "@id": "niiri:peak_0006"
      },
      {
        "prov:wasDerivedFrom": {
          "@id": "niiri:supra_threshold_cluster_0001"
        },
        "pValueFWER": "0.0",
        "equivalentZStatistic": "inf",
        "pValueUncorrected": "4.4408920985e-16",
        "rdfs:label": "Peak 0001",
        "qValueFDR": "6.3705194445e-11",
        "prov:value": {
          "@type": "xsd:float",
          "@value": "13.9346199036"
        },
        "prov:atLocation": {
          "@id": "niiri:coordinate_0001"
        },
        "@id": "niiri:peak_0001"
      },
      {
        "prov:wasDerivedFrom": {
          "@id": "niiri:supra_threshold_cluster_0003"
        },
        "pValueFWER": "4.05099727463e-06",
        "equivalentZStatistic": "6.43494304364",
        "pValueUncorrected": "6.17598194808e-11",
        "rdfs:label": "Peak 0007",
        "qValueFDR": "0.00046313051786",
        "prov:value": {
          "@type": "xsd:float",
          "@value": "7.49709033966"
        },
        "prov:atLocation": {
          "@id": "niiri:coordinate_0007"
        },
        "@id": "niiri:peak_0007"
      }
    ],
    "ResidualMeanSquaresMap": {
      "rdfs:label": "Residual Mean Squares Map",
      "prov:wasGeneratedBy": {
        "@id": "niiri:model_pe_id"
      },
      "nfo:fileName": "ResidualMeanSquares.nii.gz",
      "nidm:NIDM_0000104": {
        "@id": "niiri:coordinate_space_id_1"
      },
      "prov:atLocation": {
        "@type": "xsd:anyURI",
        "@value": "ResidualMeanSquares.nii.gz"
      },
      "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
      "@id": "niiri:residual_mean_squares_map_id",
      "dct:format": "image/nifti"
    },
    "ContrastEstimation": {
      "rdfs:label": "Contrast estimation",
      "prov:used": [
        {
          "@id": "niiri:residual_mean_squares_map_id"
        },
        {
          "@id": "niiri:contrast_id"
        },
        {
          "@id": "niiri:beta_map_id_2"
        },
        {
          "@id": "niiri:mask_id_2"
        },
        {
          "@id": "niiri:beta_map_id_1"
        },
        {
          "@id": "niiri:design_matrix_id"
        }
      ],
      "@id": "niiri:contrast_estimation_id",
      "prov:wasAssociatedWith": {
        "@id": "niiri:software_id"
      }
    },
    "ErrorModel": {
      "nidm:NIDM_0000126": {
        "@id": "nidm:NIDM_0000073"
      },
      "nidm:NIDM_0000094": true,
      "nidm:NIDM_0000101": {
        "@id": "obo:STATO_0000227"
      },
      "nidm:NIDM_0000100": {
        "@id": "nidm:NIDM_0000048"
      },
      "@id": "niiri:error_model_id",
      "nidm:NIDM_0000089": {
        "@id": "nidm:NIDM_0000073"
      }
    },
    "Data": {
      "rdfs:label": "Data",
      "prov:wasAttributedTo": [
        {
          "@id": "niiri:group2_id"
        },
        {
          "@id": "niiri:mr_scanner_id"
        },
        {
          "@id": "niiri:group_id"
        }
      ],
      "targetIntensity": "100.0",
      "@id": "niiri:data_id",
      "nidm:NIDM_0000096": true,
      "nidm:NIDM_0000172": {
        "@id": "nlx:birnlex_2250"
      }
    },
    "ReselsPerVoxelMap": [
      {
        "nfo:fileName": "RPV.img",
        "nidm:NIDM_0000103": {
          "@id": "niiri:original_rpv_map_header_id"
        },
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
        "@id": "niiri:resels_per_voxel_map_id_der",
        "dct:format": "image/nifti"
      },
      {
        "prov:wasDerivedFrom": {
          "@id": "niiri:resels_per_voxel_map_id_der"
        },
        "rdfs:label": "Resels per Voxel Map",
        "prov:wasGeneratedBy": {
          "@id": "niiri:model_pe_id"
        },
        "nfo:fileName": "ReselsPerVoxel.nii.gz",
        "nidm:NIDM_0000104": {
          "@id": "niiri:coordinate_space_id_1"
        },
        "prov:atLocation": {
          "@type": "xsd:anyURI",
          "@value": "ReselsPerVoxel.nii.gz"
        },
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
        "@id": "niiri:resels_per_voxel_map_id",
        "dct:format": "image/nifti"
      }
    ],
    "NIDMResultsExport": {
      "rdfs:label": "NIDM-Results export",
      "@id": "niiri:export_id",
      "prov:wasAssociatedWith": {
        "@id": "niiri:exporter_id"
      }
    },
    "Magnetic resonance imaging scanner": {
      "rdfs:label": "MRI Scanner",
      "@id": "niiri:mr_scanner_id",
      "@type": "Imaging instrument"
    },
    "ModelParameterEstimation": {
      "rdfs:label": "Model parameters estimation",
      "prov:used": [
        {
          "@id": "niiri:mask_id_1"
        },
        {
          "@id": "niiri:data_id"
        },
        {
          "@id": "niiri:error_model_id"
        },
        {
          "@id": "niiri:design_matrix_id"
        }
      ],
      "prov:wasAssociatedWith": {
        "@id": "niiri:software_id"
      },
      "nidm:NIDM_0000134": {
        "@id": "obo:STATO_0000370"
      },
      "@id": "niiri:model_pe_id"
    },
    "DisplayMaskMap": {
      "rdfs:label": "Display Mask Map",
      "nfo:fileName": "DisplayMask.nii.gz",
      "nidm:NIDM_0000104": {
        "@id": "niiri:coordinate_space_id_2"
      },
      "prov:atLocation": {
        "@type": "xsd:anyURI",
        "@value": "DisplayMask.nii.gz"
      },
      "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
      "@id": "niiri:display_map_id",
      "dct:format": "image/nifti"
    },
    "ContrastWeightMatrix": {
      "rdfs:label": "Contrast: Listening > Rest",
      "prov:value": "[ 1, 0, 0 ]",
      "nidm:NIDM_0000123": {
        "@id": "obo:STATO_0000176"
      },
      "nidm:NIDM_0000085": "listening > rest",
      "@id": "niiri:contrast_id"
    },
    "http://purl.org/dc/dcmitype/Image": [
      {
        "nfo:fileName": "MaximumIntensityProjection.png",
        "prov:atLocation": {
          "@type": "xsd:anyURI",
          "@value": "MaximumIntensityProjection.png"
        },
        "@id": "niiri:maximum_intensity_projection_id",
        "dct:format": "image/png"
      },
      {
        "nfo:fileName": "DesignMatrix.png",
        "prov:atLocation": {
          "@type": "xsd:anyURI",
          "@value": "DesignMatrix.png"
        },
        "@id": "niiri:design_matrix_png_id",
        "dct:format": "image/png"
      }
    ],
    "NIDMResults": {
      "rdfs:label": "NIDM-Results",
      "prov:qualifiedGeneration": {
        "@id": "_:fbfe9825b225641a29fc0e8ac5eb8d33cb1"
      },
      "@id": "niiri:spm_results_id",
      "nidm:NIDM_0000127": "1.3.0"
    },
    "Coordinate": [
      {
        "nidm:NIDM_0000086": "[ 57, -40, 7 ]",
        "rdfs:label": "Coordinate: 0006",
        "@id": "niiri:coordinate_0006"
      },
      {
        "nidm:NIDM_0000086": "[ 36, -31, -14 ]",
        "rdfs:label": "Coordinate: 0007",
        "@id": "niiri:coordinate_0007"
      },
      {
        "nidm:NIDM_0000086": "[ 57, -22, 13 ]",
        "rdfs:label": "Coordinate: 0004",
        "@id": "niiri:coordinate_0004"
      },
      {
        "nidm:NIDM_0000086": "[ 66, -13, -2 ]",
        "rdfs:label": "Coordinate: 0005",
        "@id": "niiri:coordinate_0005"
      },
      {
        "nidm:NIDM_0000086": "[ -66, -13, 4 ]",
        "rdfs:label": "Coordinate: 0002",
        "@id": "niiri:coordinate_0002"
      },
      {
        "nidm:NIDM_0000086": "[ -63, -7, -2 ]",
        "rdfs:label": "Coordinate: 0003",
        "@id": "niiri:coordinate_0003"
      },
      {
        "nidm:NIDM_0000086": "[ -60, -28, 13 ]",
        "rdfs:label": "Coordinate: 0001",
        "@id": "niiri:coordinate_0001"
      }
    ],
    "ContrastMap": [
      {
        "nfo:fileName": "con_0001.img",
        "nidm:NIDM_0000103": {
          "@id": "niiri:original_contrast_map_header_id"
        },
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
        "@id": "niiri:contrast_map_id_der",
        "dct:format": "image/nifti"
      },
      {
        "prov:wasDerivedFrom": {
          "@id": "niiri:contrast_map_id_der"
        },
        "rdfs:label": "Contrast Map: listening > rest",
        "prov:wasGeneratedBy": {
          "@id": "niiri:contrast_estimation_id"
        },
        "nidm:NIDM_0000104": {
          "@id": "niiri:coordinate_space_id_1"
        },
        "nfo:fileName": "Contrast.nii.gz",
        "nidm:NIDM_0000085": "listening > rest",
        "prov:atLocation": {
          "@type": "xsd:anyURI",
          "@value": "Contrast.nii.gz"
        },
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
        "@id": "niiri:contrast_map_id",
        "dct:format": "image/nifti"
      }
    ],
    "ClusterDefinitionCriteria": {
      "nidm:NIDM_0000099": {
        "@id": "nidm:NIDM_0000128"
      },
      "@id": "niiri:cluster_definition_criteria_id",
      "rdfs:label": "Cluster Connectivity Criterion: 18"
    },
    "Inference": {
      "rdfs:label": "Inference",
      "prov:used": [
        {
          "@id": "niiri:mask_id_3"
        },
        {
          "@id": "niiri:extent_threshold_id"
        },
        {
          "@id": "niiri:cluster_definition_criteria_id"
        },
        {
          "@id": "niiri:mask_id_2"
        },
        {
          "@id": "niiri:peak_definition_criteria_id"
        },
        {
          "@id": "niiri:height_threshold_id"
        },
        {
          "@id": "niiri:statistic_map_id"
        },
        {
          "@id": "niiri:resels_per_voxel_map_id"
        }
      ],
      "prov:wasAssociatedWith": {
        "@id": "niiri:software_id"
      },
      "nidm:NIDM_0000097": {
        "@id": "nidm:NIDM_0000060"
      },
      "@id": "niiri:inference_id"
    },
    "ClusterLabelsMap": {
      "rdfs:label": "Cluster Labels Map",
      "nfo:fileName": "ClusterLabels.nii.gz",
      "nidm:NIDM_0000104": {
        "@id": "niiri:coordinate_space_id_1"
      },
      "prov:atLocation": {
        "@type": "xsd:anyURI",
        "@value": "ClusterLabels.nii.gz"
      },
      "crypto:sha512": "13093aae03897e2518307d000eb298f4b1439814d8d3d77c622b717423f93506dd5de5669513ab65c6dd74a7d27ee9df08620f546ed00575517b40e5878c2c96",
      "@id": "niiri:cluster_label_map_id",
      "dct:format": "image/nifti"
    },
    "StatisticMap": [
      {
        "prov:wasDerivedFrom": {
          "@id": "niiri:statistic_map_id_der"
        },
        "rdfs:label": "T-Statistic Map: listening > rest",
        "prov:wasGeneratedBy": {
          "@id": "niiri:contrast_estimation_id"
        },
        "errorDegreesOfFreedom": "72.9999999991",
        "nidm:NIDM_0000104": {
          "@id": "niiri:coordinate_space_id_1"
        },
        "nfo:fileName": "TStatistic.nii.gz",
        "nidm:NIDM_0000123": {
          "@id": "obo:STATO_0000176"
        },
        "nidm:NIDM_0000085": "listening > rest",
        "prov:atLocation": {
          "@type": "xsd:anyURI",
          "@value": "TStatistic.nii.gz"
        },
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
        "effectDegreesOfFreedom": "1.0",
        "@id": "niiri:statistic_map_id",
        "dct:format": "image/nifti"
      },
      {
        "nfo:fileName": "spmT_0001.img",
        "nidm:NIDM_0000103": {
          "@id": "niiri:statistic_original_map_header_id"
        },
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
        "@id": "niiri:statistic_map_id_der",
        "dct:format": "image/nifti"
      }
    ],
    "ContrastStandardErrorMap": {
      "rdfs:label": "Contrast Standard Error Map",
      "prov:wasGeneratedBy": {
        "@id": "niiri:contrast_estimation_id"
      },
      "nfo:fileName": "ContrastStandardError.nii.gz",
      "nidm:NIDM_0000104": {
        "@id": "niiri:coordinate_space_id_1"
      },
      "prov:atLocation": {
        "@type": "xsd:anyURI",
        "@value": "ContrastStandardError.nii.gz"
      },
      "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
      "@id": "niiri:contrast_standard_error_map_id",
      "dct:format": "image/nifti"
    },
    "prov:Entity": [
      {
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a...",
        "nfo:fileName": "RPV.hdr",
        "@id": "niiri:original_rpv_map_header_id",
        "@type": "MapHeader",
        "dct:format": "image/nifti"
      },
      {
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a...",
        "nfo:fileName": "beta_0001.hdr",
        "@id": "niiri:original_pe_map_header_id",
        "@type": "MapHeader",
        "dct:format": "image/nifti"
      },
      {
        "crypto:sha512": "e43b6e01b0463fe7d40782137867a...",
        "nfo:fileName": "spmT_0001.hdr",
        "@id": "niiri:statistic_original_map_header_id",
        "@type": "MapHeader",
        "dct:format": "image/nifti"
      }
    ],
    "SearchSpaceMaskMap": {
      "nidm:NIDM_0000157": "[ 8.87643567497404, 8.89885340008753, 7.83541276878791 ]",
      "heightCriticalThresholdFDR05": "6.22537899017",
      "nidm:NIDM_0000159": "[ 2.95881189165801, 2.96628446669584, 2.61180425626264 ]",
      "smallestSignificantClusterSizeInVoxelsFDR05": "3",
      "nfo:fileName": "SearchSpaceMask.nii.gz",
      "searchVolumeInResels": "2552.68032522",
      "prov:atLocation": {
        "@type": "xsd:anyURI",
        "@value": "SearchSpaceMask.nii.gz"
      },
      "searchVolumeInVoxels": "65593",
      "prov:wasGeneratedBy": {
        "@id": "niiri:inference_id"
      },
      "expectedNumberOfClusters": "0.088917268796",
      "crypto:sha512": "e43b6e01b0463fe7d40782137867a",
      "rdfs:label": "Search Space Mask Map",
      "heightCriticalThresholdFWE05": "5.23529984739",
      "@id": "niiri:search_space_mask_id",
      "smallestSignificantClusterSizeInVoxelsFWE05": "1",
      "expectedNumberOfVoxelsPerCluster": "0.553331387916",
      "reselSizeInVoxels": "22.922964314",
      "http://purl.org/nidash/spm#SPM_0000010": "[3, 72.3216126440484, 850.716735116472, 2552.68032521656]",
      "nidm:NIDM_0000120": false,
      "nidm:NIDM_0000104": {
        "@id": "niiri:coordinate_space_id_2"
      },
      "searchVolumeInUnits": "1771011.0",
      "dct:format": "image/nifti"
    },
    "spm": {
      "rdfs:label": "spm_results_nidm",
      "nidm:NIDM_0000122": "12b.5858",
      "@id": "niiri:exporter_id"
    }
  }
}
"""


@with_tree(tree={'nidm_minimal.json': example_metadata})
@with_tempfile(mkdir=True)
def test_nidm(packpath, dspath):
    # create a fake NIDMresult pack
    ds = Dataset(dspath).create()
    make_archive(
        op.join(dspath, 'myfake.nidm'),
        'zip',
        packpath)
    ds.add('.')
    ds.run_procedure(['cfg_metadatatypes', 'nidmresults'])
    ok_clean_git(dspath)

    # engage the extractor(s)
    res = ds.aggregate_metadata()
    # aggregation done without whining
    assert_status('ok', res)
    res = ds.metadata(reporton='files')
    assert_result_count(res, 1)
    assert_result_count(res, 1, path=op.join(ds.path, 'myfake.nidm.zip'))
    # TODO test the actual metadata content, but not now, as it will will
    # soon to another structure

    # unique metadata values include nidm results
    res = ds.metadata(reporton='datasets')
    assert_result_count(res, 1)
    res = res[0]
    assert_in(
        'nidmresults',
        res['metadata']['datalad_unique_content_properties'])
    assert_in(
        'records',
        res['metadata']['datalad_unique_content_properties']['nidmresults'])
