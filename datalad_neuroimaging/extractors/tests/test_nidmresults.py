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
   "records" : {
      "SupraThresholdCluster" : [
         {
            "@id" : "niiri:supra_threshold_cluster_0001",
            "clusterSizeInResels" : "6.31265696809113",
            "qValueFDR" : "1.77948412240239e-18",
            "rdfs:label" : "Supra-Threshold Cluster: 0001",
            "clusterLabelId" : "1",
            "@type" : "Entity",
            "clusterSizeInVoxels" : "839",
            "pValueUncorrected" : "3.55896824480477e-19",
            "pValueFWER" : "0.0",
            "wasDerivedFrom" : "niiri:excursion_set_map_id"
         },
         {
            "pValueFWER" : "0.0",
            "pValueUncorrected" : "5.34280282632073e-17",
            "clusterSizeInVoxels" : "695",
            "wasDerivedFrom" : "niiri:excursion_set_map_id",
            "qValueFDR" : "1.33570070658018e-16",
            "rdfs:label" : "Supra-Threshold Cluster: 0002",
            "clusterLabelId" : "2",
            "@id" : "niiri:supra_threshold_cluster_0002",
            "clusterSizeInResels" : "5.22919736927692",
            "@type" : "Entity"
         }
      ],
      "FWERadjustedpvalue" : [
         {
            "@id" : "niiri:height_threshold_id",
            "rdfs:label" : "Height Threshold: p<0.050000 (FWE)",
            "prov:value" : {
               "@value" : "0.05",
               "@type" : "xsd:float"
            },
            "@type" : [
               "HeightThreshold",
               "Entity"
            ],
            "equivalentThreshold" : [
               "niiri:height_threshold_id_3",
               "niiri:height_threshold_id_2"
            ]
         },
         {
            "prov:value" : {
               "@type" : "xsd:float",
               "@value" : "1.0"
            },
            "@type" : [
               "Entity",
               "ExtentThreshold"
            ],
            "rdfs:label" : "Extent Threshold",
            "@id" : "niiri:extent_threshold_id_2"
         }
      ],
      "PValueUncorrected" : {
         "@type" : [
            "ExtentThreshold",
            "Entity"
         ],
         "prov:value" : {
            "@value" : "1.0",
            "@type" : "xsd:float"
         },
         "rdfs:label" : "Extent Threshold",
         "@id" : "niiri:extent_threshold_id_3"
      },
      "StatisticMap" : [
         {
            "@type" : "Entity",
            "inCoordinateSpace" : "niiri:coordinate_space_id_1",
            "rdfs:label" : "T-Statistic Map: passive listening > rest",
            "effectDegreesOfFreedom" : "1.0",
            "@id" : "niiri:statistic_map_id",
            "wasDerivedFrom" : "niiri:statistic_map_id_der",
            "location" : "TStatistic.nii.gz",
            "dct:format" : "image/nifti",
            "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#sha512" : "799e9bbf8c15b35c0098bca468846bf2cd895a3366382b5ceaa953f1e9e576955341a7c86e13e6fe9359da4ff1496a609f55ce9ecff8da2e461365372f2506d6",
            "statisticType" : "http://purl.obolibrary.org/obo/STATO_0000176",
            "wasGeneratedBy" : "niiri:contrast_estimation_id",
            "nidm:NIDM_0000085" : "passive listening > rest",
            "nfo:fileName" : "TStatistic.nii.gz",
            "errorDegreesOfFreedom" : "84.0"
         },
         {
            "dct:format" : "image/nifti",
            "@type" : "Entity",
            "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#sha512" : "55951f31f0ede7e88eca5cd4793df3f630aba21bc90fb81e3695db060c7d4c0b0ccf0b51fd8958c32ea3253d3122e9b31a54262bf910f8b5b646054ceb9a5825",
            "nfo:fileName" : "spmT_0001.nii",
            "@id" : "niiri:statistic_map_id_der"
         }
      ],
      "Location" : [
         {
            "@id" : "niiri:coordinate_0007",
            "rdfs:label" : "Coordinate: 0007",
            "@type" : [
               "Coordinate",
               "Entity"
            ],
            "nidm:NIDM_0000086" : "[ 36, -28, -13 ]"
         },
         {
            "nidm:NIDM_0000086" : "[ -42, -31, 11 ]",
            "@type" : [
               "Coordinate",
               "Entity"
            ],
            "rdfs:label" : "Coordinate: 0002",
            "@id" : "niiri:coordinate_0002"
         },
         {
            "@type" : [
               "Coordinate",
               "Entity"
            ],
            "nidm:NIDM_0000086" : "[ 57, -40, 5 ]",
            "@id" : "niiri:coordinate_0006",
            "rdfs:label" : "Coordinate: 0006"
         }
      ],
      "Magneticresonanceimagingscanner" : {
         "rdfs:label" : "MRI Scanner",
         "@id" : "niiri:mr_scanner_id",
         "@type" : [
            "Agent",
            "Imaginginstrument"
         ]
      },
      "DesignMatrix" : {
         "dct:format" : "text/csv",
         "location" : "DesignMatrix.csv",
         "nfo:fileName" : "DesignMatrix.csv",
         "@type" : "Entity",
         "hasDriftModel" : "niiri:drift_model_id",
         "nidm:NIDM_0000021" : "[\\"Sn(1) active*bf(1)\\", \\"Sn(1) constant\\"]",
         "Description" : "niiri:design_matrix_png_id",
         "@id" : "niiri:design_matrix_id",
         "hasHRFBasis" : "spm:SPM_0000004",
         "rdfs:label" : "Design Matrix"
      },
      "Person" : {
         "@type" : "Agent",
         "rdfs:label" : "Person",
         "@id" : "niiri:subject_id"
      },
      "ContrastStandardErrorMap" : {
         "nfo:fileName" : "ContrastStandardError.nii.gz",
         "location" : "ContrastStandardError.nii.gz",
         "dct:format" : "image/nifti",
         "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#sha512" : "f4e3616579fe8b0812469409b1501e391bb17ca6e364f37d622b37fa9014cf1dd89befece07e73cf5bca5b3116f55ac4496751ca990db85e8377001a4be941b2",
         "wasGeneratedBy" : "niiri:contrast_estimation_id",
         "inCoordinateSpace" : "niiri:coordinate_space_id_1",
         "rdfs:label" : "Contrast Standard Error Map",
         "@id" : "niiri:contrast_standard_error_map_id",
         "@type" : "Entity"
      },
      "Activity" : [
         {
            "@type" : "ContrastEstimation",
            "used" : [
               "niiri:design_matrix_id",
               "niiri:contrast_id",
               "niiri:beta_map_id_1",
               "niiri:residual_mean_squares_map_id",
               "niiri:mask_id_1",
               "niiri:beta_map_id_2"
            ],
            "rdfs:label" : "Contrast estimation",
            "wasAssociatedWith" : "niiri:software_id",
            "@id" : "niiri:contrast_estimation_id"
         },
         {
            "@type" : "NIDMResultsExport",
            "rdfs:label" : "NIDM-Results export",
            "@id" : "niiri:export_id",
            "wasAssociatedWith" : "niiri:exporter_id"
         },
         {
            "@type" : "Inference",
            "used" : [
               "niiri:statistic_map_id",
               "niiri:height_threshold_id",
               "niiri:cluster_definition_criteria_id",
               "niiri:resels_per_voxel_map_id",
               "niiri:extent_threshold_id",
               "niiri:mask_id_1",
               "niiri:peak_definition_criteria_id"
            ],
            "hasAlternativeHypothesis" : "nidm:NIDM_0000060",
            "wasAssociatedWith" : "niiri:software_id",
            "@id" : "niiri:inference_id",
            "rdfs:label" : "Inference"
         }
      ],
      "ClusterLabelsMap" : {
         "@type" : "Entity",
         "@id" : "niiri:cluster_label_map_id",
         "rdfs:label" : "Cluster Labels Map",
         "inCoordinateSpace" : "niiri:coordinate_space_id_1",
         "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#sha512" : "a132bb284da461fd9e20eb2986373a9171c90a342c1e694297bc02f5674a311a560b7ff34bdf045dc191d4afff8c690a373db6408c1fe93f7c25e23707ce65c3",
         "dct:format" : "image/nifti",
         "location" : "ClusterLabels.nii.gz",
         "nfo:fileName" : "ClusterLabels.nii.gz"
      },
      "ErrorModel" : {
         "hasErrorDistribution" : "http://purl.obolibrary.org/obo/STATO_0000227",
         "@type" : "Entity",
         "nidm:NIDM_0000094" : true,
         "hasErrorDependence" : "http://purl.obolibrary.org/obo/STATO_0000357",
         "@id" : "niiri:error_model_id",
         "dependenceMapWiseDependence" : "nidm:NIDM_0000072",
         "varianceMapWiseDependence" : "nidm:NIDM_0000073"
      },
      "Agent" : {
         "@type" : [
            "SoftwareAgent",
            "SPM"
         ],
         "softwareVersion" : "12.12.1",
         "rdfs:label" : "SPM",
         "@id" : "niiri:software_id"
      },
      "Peak" : [
         {
            "wasDerivedFrom" : "niiri:supra_threshold_cluster_0001",
            "pValueUncorrected" : "4.44089209850063e-16",
            "pValueFWER" : "7.69451169446711e-12",
            "equivalentZStatistic" : "inf",
            "atLocation" : "niiri:coordinate_0003",
            "@type" : "Entity",
            "prov:value" : {
               "@type" : "xsd:float",
               "@value" : "10.2856016159058"
            },
            "@id" : "niiri:peak_0003",
            "qValueFDR" : "6.84121260274992e-10",
            "rdfs:label" : "Peak: 0003"
         },
         {
            "pValueFWER" : "6.9250605250204e-11",
            "equivalentZStatistic" : "inf",
            "pValueUncorrected" : "1.22124532708767e-15",
            "wasDerivedFrom" : "niiri:supra_threshold_cluster_0002",
            "qValueFDR" : "6.52169693024352e-09",
            "rdfs:label" : "Peak: 0006",
            "@id" : "niiri:peak_0006",
            "atLocation" : "niiri:coordinate_0006",
            "@type" : "Entity",
            "prov:value" : {
               "@value" : "9.72103404998779",
               "@type" : "xsd:float"
            }
         },
         {
            "prov:value" : {
               "@value" : "5.27320194244385",
               "@type" : "xsd:float"
            },
            "atLocation" : "niiri:coordinate_0009",
            "@type" : "Entity",
            "rdfs:label" : "Peak: 0009",
            "qValueFDR" : "0.251554254717758",
            "@id" : "niiri:peak_0009",
            "wasDerivedFrom" : "niiri:supra_threshold_cluster_0005",
            "equivalentZStatistic" : "4.88682085490477",
            "pValueFWER" : "0.0119099090973821",
            "pValueUncorrected" : "5.12386299833523e-07"
         }
      ],
      "ParameterEstimateMap" : [
         {
            "@id" : "niiri:beta_map_id_2_der",
            "nfo:fileName" : "beta_0002.nii",
            "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#sha512" : "3f72b788762d9ab2c7ddb5e4d446872694ee42fc8897fe5317b54efb7924f784da6499065db897a49595d8763d1893ad65ad102b0c88f2e72e2d028173343008",
            "@type" : "Entity",
            "dct:format" : "image/nifti"
         },
         {
            "dct:format" : "image/nifti",
            "@type" : "Entity",
            "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#sha512" : "fab2573099693215bac756bc796fbc983524473dec5c1b2d66fb83694c17412731df7f574094cb6c4a77994af7be11ed9aa545090fbe8ec6565a5c3c3dae8f0f",
            "nfo:fileName" : "beta_0001.nii",
            "@id" : "niiri:beta_map_id_1_der"
         }
      ],
      "ContrastMap" : {
         "nfo:fileName" : "Contrast.nii.gz",
         "location" : "Contrast.nii.gz",
         "wasDerivedFrom" : "niiri:contrast_map_id_der",
         "dct:format" : "image/nifti",
         "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#sha512" : "f0720b732aaf19c2ec42d0469f8308beb3aa978baf65c7dce6476a0d8e5b2f38c4fa9609f045a536678440feebce9a047e3bd6d59fdb8fb64baae058690bbda2",
         "nidm:NIDM_0000085" : "passive listening > rest",
         "wasGeneratedBy" : "niiri:contrast_estimation_id",
         "inCoordinateSpace" : "niiri:coordinate_space_id_1",
         "rdfs:label" : "Contrast Map: passive listening > rest",
         "@id" : "niiri:contrast_map_id",
         "@type" : "Entity"
      },
      "ModelParameterEstimation" : {
         "wasAssociatedWith" : "niiri:software_id",
         "@id" : "niiri:model_pe_id",
         "withEstimationMethod" : "http://purl.obolibrary.org/obo/STATO_0000372",
         "rdfs:label" : "Model parameters estimation",
         "@type" : "Activity",
         "used" : [
            "niiri:data_id",
            "niiri:error_model_id",
            "niiri:design_matrix_id"
         ]
      },
      "HeightThreshold" : [
         {
            "@type" : [
               "Entity",
               "statistic"
            ],
            "prov:value" : {
               "@value" : "4.85241745689539",
               "@type" : "xsd:float"
            },
            "rdfs:label" : "Height Threshold",
            "@id" : "niiri:height_threshold_id_2"
         },
         {
            "@id" : "niiri:height_threshold_id_3",
            "rdfs:label" : "Height Threshold",
            "prov:value" : {
               "@type" : "xsd:float",
               "@value" : "2.7772578456986e-06"
            },
            "@type" : [
               "Entity",
               "PValueUncorrected"
            ]
         }
      ],
      "SoftwareAgent" : {
         "@id" : "niiri:exporter_id",
         "rdfs:label" : "spm_results_nidm",
         "@type" : [
            "spm_results_nidm",
            "Agent"
         ],
         "softwareVersion" : "12b.5858"
      },
      "Entity" : [
         {
            "prov:value" : {
               "@type" : "xsd:float",
               "@value" : "6.19558477401733"
            },
            "atLocation" : "niiri:coordinate_0008",
            "@type" : "Peak",
            "@id" : "niiri:peak_0008",
            "qValueFDR" : "0.00949154522981781",
            "rdfs:label" : "Peak: 0008",
            "wasDerivedFrom" : "niiri:supra_threshold_cluster_0004",
            "pValueUncorrected" : "1.0325913235576e-08",
            "equivalentZStatistic" : "5.60645028016544",
            "pValueFWER" : "0.000382453907303626"
         },
         {
            "nfo:fileName" : "GrandMean.nii.gz",
            "maskedMedian" : "132.008995056152",
            "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#sha512" : "4d3528031bce4a9c1b994b8124e6e0eddb9df90b49c84787652ed94df8c14c04ec92100a2d8ea86a8df24ba44617aca7457ddcb2f42253fc17e33296a1aea1cb",
            "wasGeneratedBy" : "niiri:model_pe_id",
            "location" : "GrandMean.nii.gz",
            "dct:format" : "image/nifti",
            "@id" : "niiri:grand_mean_map_id",
            "inCoordinateSpace" : "niiri:coordinate_space_id_1",
            "rdfs:label" : "Grand Mean Map",
            "@type" : "GrandMeanMap"
         },
         {
            "@id" : "niiri:resels_per_voxel_map_id_der",
            "nfo:fileName" : "RPV.nii",
            "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#sha512" : "963283cdde607c40e4640c27453867bd0d70133b6d61482933862487c0f4a5acdb2e338a12a2605ee044b1aa47b5717f0c520b90ed3c49b5227f0483bd48512d",
            "@type" : "ReselsPerVoxelMap",
            "dct:format" : "image/nifti"
         },
         {
            "numberOfDimensions" : "3",
            "nidm:NIDM_0000090" : "[ 53, 63, 52 ]",
            "nidm:NIDM_0000132" : "[[-3, 0, 0, 78],[0, 3, 0, -112],[0, 0, 3, -70],[0, 0, 0, 1]]",
            "rdfs:label" : "Coordinate space 1",
            "@id" : "niiri:coordinate_space_id_1",
            "inWorldCoordinateSystem" : "nidm:NIDM_0000050",
            "nidm:NIDM_0000131" : "[ 3, 3, 3 ]",
            "nidm:NIDM_0000133" : "[ \\"mm\\", \\"mm\\", \\"mm\\" ]",
            "@type" : "CoordinateSpace"
         },
         {
            "nfo:fileName" : "mask.nii",
            "@id" : "niiri:mask_id_1_der",
            "dct:format" : "image/nifti",
            "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#sha512" : "fbc254cab29db5532feccce554ec9d3c845197eca9013ec9f0efd5d8d56e3aa008ccee4038fb3651d30447fa0f316938b07c3ad961b623458dcd9b46968a8e11",
            "@type" : "MaskMap"
         },
         {
            "rdfs:label" : "Cluster Connectivity Criterion: 18",
            "@id" : "niiri:cluster_definition_criteria_id",
            "@type" : "ClusterDefinitionCriteria",
            "hasConnectivityCriterion" : "nidm:NIDM_0000128"
         },
         {
            "@type" : "ReselsPerVoxelMap",
            "@id" : "niiri:resels_per_voxel_map_id",
            "inCoordinateSpace" : "niiri:coordinate_space_id_1",
            "rdfs:label" : "Resels per Voxel Map",
            "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#sha512" : "2025dc6c33708b80708c2eba3215fb1149df236fb558a8e8f8f6cf34595fb54734fe5e436db3e192a424d99699dd7feb2f4a9020ceae8e7bcbd881b17825256a",
            "wasGeneratedBy" : "niiri:model_pe_id",
            "location" : "ReselsPerVoxel.nii.gz",
            "wasDerivedFrom" : "niiri:resels_per_voxel_map_id_der",
            "dct:format" : "image/nifti",
            "nfo:fileName" : "ReselsPerVoxel.nii.gz"
         },
         {
            "nidm:NIDM_0000085" : "passive listening > rest",
            "@type" : "contrastweightmatrix",
            "prov:value" : "[1, 0]",
            "statisticType" : "http://purl.obolibrary.org/obo/STATO_0000176",
            "@id" : "niiri:contrast_id",
            "rdfs:label" : "Contrast: passive listening > rest"
         },
         {
            "nfo:fileName" : "con_0001.nii",
            "@id" : "niiri:contrast_map_id_der",
            "dct:format" : "image/nifti",
            "@type" : "ContrastMap",
            "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#sha512" : "277dd1da13d391c33c172fb8c71060008cc66e173de6362eb857b0055b41e9bae57911f7ec4b45659905103b1139ebf3da0c2d04cf105bbce0cdc3004b643c22"
         },
         {
            "wasDerivedFrom" : "niiri:excursion_set_map_id",
            "clusterSizeInVoxels" : "29",
            "pValueUncorrected" : "0.0110257032104773",
            "pValueFWER" : "0.000565384750377596",
            "@type" : "SupraThresholdCluster",
            "clusterSizeInResels" : "0.218196724761195",
            "@id" : "niiri:supra_threshold_cluster_0004",
            "rdfs:label" : "Supra-Threshold Cluster: 0004",
            "qValueFDR" : "0.0137821290130967",
            "clusterLabelId" : "4"
         },
         {
            "qValueFDR" : "0.00257605396646668",
            "rdfs:label" : "Peak: 0007",
            "@id" : "niiri:peak_0007",
            "@type" : "Peak",
            "atLocation" : "niiri:coordinate_0007",
            "prov:value" : {
               "@value" : "6.55745935440063",
               "@type" : "xsd:float"
            },
            "equivalentZStatistic" : "5.87574033699266",
            "pValueFWER" : "9.17574302586877e-05",
            "pValueUncorrected" : "2.10478867668229e-09",
            "wasDerivedFrom" : "niiri:supra_threshold_cluster_0003"
         },
         {
            "location" : "DesignMatrix.png",
            "dct:format" : "image/png",
            "@type" : "http://purl.org/dc/dcmitype/Image",
            "nfo:fileName" : "DesignMatrix.png",
            "@id" : "niiri:design_matrix_png_id"
         },
         {
            "rdfs:label" : "Coordinate: 0008",
            "@id" : "niiri:coordinate_0008",
            "nidm:NIDM_0000086" : "[ -33, -31, -16 ]",
            "@type" : [
               "Location",
               "Coordinate"
            ]
         },
         {
            "nfo:fileName" : "ExcursionSet.nii.gz",
            "hasMaximumIntensityProjection" : "niiri:maximum_intensity_projection_id",
            "numberOfSupraThresholdClusters" : "5",
            "hasClusterLabelsMap" : "niiri:cluster_label_map_id",
            "dct:format" : "image/nifti",
            "location" : "ExcursionSet.nii.gz",
            "wasGeneratedBy" : "niiri:inference_id",
            "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#sha512" : "d96b82761c299a66978893cab6034f3f8aed25d0a135636b0ffe79f4cf11becce86ba261f7aeb43717f5d0e47ad0b14cfb0402786251e3f2c507890c83b27652",
            "rdfs:label" : "Excursion Set Map",
            "inCoordinateSpace" : "niiri:coordinate_space_id_1",
            "@id" : "niiri:excursion_set_map_id",
            "@type" : "ExcursionSetMap",
            "pValue" : "2.83510681598e-09"
         },
         {
            "@type" : "ResidualMeanSquaresMap",
            "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#sha512" : "1635e0ae420cac1b5989fbc753b95f504dd957ff2986367fc4cd13ff35c44b4ee60994a9cdcab93a7d247fc5a8decb7578fa4c553b0ac905af8c7041db9b4acd",
            "dct:format" : "image/nifti",
            "@id" : "niiri:residual_mean_squares_map_id_der",
            "nfo:fileName" : "ResMS.nii"
         },
         {
            "@type" : [
               "NIDMResults",
               "Bundle"
            ],
            "nidm:NIDM_0000127" : "1.3.0",
            "@id" : "niiri:spm_results_id",
            "qualifiedGeneration" : "_:f1b4bd76338a04597b3f698e59f695e53b1",
            "rdfs:label" : "NIDM-Results"
         },
         {
            "pValueUncorrected" : "4.44089209850063e-16",
            "pValueFWER" : "0.0",
            "equivalentZStatistic" : "inf",
            "wasDerivedFrom" : "niiri:supra_threshold_cluster_0002",
            "@id" : "niiri:peak_0005",
            "qValueFDR" : "1.19156591713838e-11",
            "rdfs:label" : "Peak: 0005",
            "prov:value" : {
               "@type" : "xsd:float",
               "@value" : "12.4728717803955"
            },
            "@type" : "Peak",
            "atLocation" : "niiri:coordinate_0005"
         },
         {
            "wasDerivedFrom" : "niiri:supra_threshold_cluster_0002",
            "pValueUncorrected" : "4.44089209850063e-16",
            "equivalentZStatistic" : "inf",
            "pValueFWER" : "0.0",
            "atLocation" : "niiri:coordinate_0004",
            "@type" : "Peak",
            "prov:value" : {
               "@type" : "xsd:float",
               "@value" : "13.5425577163696"
            },
            "@id" : "niiri:peak_0004",
            "rdfs:label" : "Peak: 0004",
            "qValueFDR" : "1.19156591713838e-11"
         },
         {
            "nfo:fileName" : "ResidualMeanSquares.nii.gz",
            "wasDerivedFrom" : "niiri:residual_mean_squares_map_id_der",
            "location" : "ResidualMeanSquares.nii.gz",
            "dct:format" : "image/nifti",
            "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#sha512" : "84cd0e608b8763307a1166b88761291e552838d85b58334a69a286060f6489a3b0929a940c3ccac883803455118787ea32e0bb5a6d236a5d6e9e8b6a9f918a6b",
            "wasGeneratedBy" : "niiri:model_pe_id",
            "inCoordinateSpace" : "niiri:coordinate_space_id_1",
            "rdfs:label" : "Residual Mean Squares Map",
            "@id" : "niiri:residual_mean_squares_map_id",
            "@type" : "ResidualMeanSquaresMap"
         },
         {
            "@type" : "DiscreteCosineTransformbasisDriftModel",
            "rdfs:label" : "SPM's DCT Drift Model",
            "spm:SPM_0000001" : {
               "@type" : "xsd:float",
               "@value" : "128.0"
            },
            "@id" : "niiri:drift_model_id"
         },
         {
            "equivalentZStatistic" : "inf",
            "pValueFWER" : "0.0",
            "pValueUncorrected" : "4.44089209850063e-16",
            "wasDerivedFrom" : "niiri:supra_threshold_cluster_0001",
            "qValueFDR" : "1.19156591713838e-11",
            "rdfs:label" : "Peak: 0001",
            "@id" : "niiri:peak_0001",
            "prov:value" : {
               "@value" : "17.5207633972168",
               "@type" : "xsd:float"
            },
            "atLocation" : "niiri:coordinate_0001",
            "@type" : "Peak"
         },
         {
            "dct:format" : "image/png",
            "location" : "MaximumIntensityProjection.png",
            "@type" : "http://purl.org/dc/dcmitype/Image",
            "nfo:fileName" : "MaximumIntensityProjection.png",
            "@id" : "niiri:maximum_intensity_projection_id"
         },
         {
            "pValueUncorrected" : "0.0818393184514307",
            "clusterSizeInVoxels" : "12",
            "pValueFWER" : "0.00418900977248904",
            "wasDerivedFrom" : "niiri:excursion_set_map_id",
            "@id" : "niiri:supra_threshold_cluster_0005",
            "clusterSizeInResels" : "0.0902882999011843",
            "clusterLabelId" : "5",
            "rdfs:label" : "Supra-Threshold Cluster: 0005",
            "qValueFDR" : "0.0818393184514307",
            "@type" : "SupraThresholdCluster"
         },
         {
            "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#sha512" : "3f72b788762d9ab2c7ddb5e4d446872694ee42fc8897fe5317b54efb7924f784da6499065db897a49595d8763d1893ad65ad102b0c88f2e72e2d028173343008",
            "wasGeneratedBy" : "niiri:model_pe_id",
            "wasDerivedFrom" : "niiri:beta_map_id_2_der",
            "location" : "ParameterEstimate_0002.nii.gz",
            "dct:format" : "image/nifti",
            "nfo:fileName" : "ParameterEstimate_0002.nii.gz",
            "@type" : "ParameterEstimateMap",
            "@id" : "niiri:beta_map_id_2",
            "inCoordinateSpace" : "niiri:coordinate_space_id_1",
            "rdfs:label" : "Parameter Estimate Map 2"
         },
         {
            "@id" : "niiri:peak_definition_criteria_id",
            "rdfs:label" : "Peak Definition Criteria",
            "minDistanceBetweenPeaks" : "8.0",
            "maxNumberOfPeaksPerCluster" : "3",
            "@type" : "PeakDefinitionCriteria"
         },
         {
            "@type" : "ParameterEstimateMap",
            "inCoordinateSpace" : "niiri:coordinate_space_id_1",
            "rdfs:label" : "Parameter Estimate Map 1",
            "@id" : "niiri:beta_map_id_1",
            "location" : "ParameterEstimate_0001.nii.gz",
            "wasDerivedFrom" : "niiri:beta_map_id_1_der",
            "dct:format" : "image/nifti",
            "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#sha512" : "fab2573099693215bac756bc796fbc983524473dec5c1b2d66fb83694c17412731df7f574094cb6c4a77994af7be11ed9aa545090fbe8ec6565a5c3c3dae8f0f",
            "wasGeneratedBy" : "niiri:model_pe_id",
            "nfo:fileName" : "ParameterEstimate_0001.nii.gz"
         },
         {
            "smallestSignificantClusterSizeInVoxelsFWE05" : "12",
            "expectedNumberOfVoxelsPerCluster" : "4.02834655908613",
            "nidm:NIDM_0000157" : "[ 16.2383695773208, 16.3091687172086, 13.5499997663244 ]",
            "@id" : "niiri:search_space_mask_id",
            "dct:format" : "image/nifti",
            "reselSizeInVoxels" : "132.907586178202",
            "searchVolumeInVoxels" : "69306",
            "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#sha512" : "932fd9f0d55e9822748f4a9b35a0a7f0fe442f3e061e2eda48c2617a2938df50ea84deca8de0725641a0105b712a80a0c8931df9bdf3bef788b1041379d00875",
            "smallestSignificantClusterSizeInVoxelsFDR05" : "29",
            "heightCriticalThresholdFWE05" : "4.85241745689539",
            "@type" : "SearchSpaceMaskMap",
            "rdfs:label" : "Search Space Mask Map",
            "inCoordinateSpace" : "niiri:coordinate_space_id_1",
            "searchVolumeInResels" : "467.07642343881",
            "nidm:NIDM_0000120" : true,
            "location" : "SearchSpaceMask.nii.gz",
            "nidm:NIDM_0000159" : "[ 5.41278985910694, 5.43638957240286, 4.51666658877481 ]",
            "wasGeneratedBy" : "niiri:inference_id",
            "expectedNumberOfClusters" : "0.0512932943875478",
            "spm:SPM_0000010" : "[7, 42.96312274763, 269.40914815306, 467.07642343881]",
            "nfo:fileName" : "SearchSpaceMask.nii.gz",
            "heightCriticalThresholdFDR05" : "5.7639536857605",
            "searchVolumeInUnits" : "1871262.0"
         },
         {
            "@id" : "niiri:supra_threshold_cluster_0003",
            "clusterSizeInResels" : "0.278388924695318",
            "rdfs:label" : "Supra-Threshold Cluster: 0003",
            "qValueFDR" : "0.00829922079256674",
            "clusterLabelId" : "3",
            "@type" : "SupraThresholdCluster",
            "pValueUncorrected" : "0.00497953247554004",
            "clusterSizeInVoxels" : "37",
            "pValueFWER" : "0.000255384009130943",
            "wasDerivedFrom" : "niiri:excursion_set_map_id"
         },
         {
            "wasDerivedFrom" : "niiri:supra_threshold_cluster_0001",
            "pValueUncorrected" : "4.44089209850063e-16",
            "pValueFWER" : "0.0",
            "equivalentZStatistic" : "inf",
            "@type" : "Peak",
            "atLocation" : "niiri:coordinate_0002",
            "prov:value" : {
               "@type" : "xsd:float",
               "@value" : "13.0321407318"
            },
            "@id" : "niiri:peak_0002",
            "qValueFDR" : "1.19156591714e-11",
            "rdfs:label" : "Peak: 0002"
         }
      ],
      "ExtentThreshold" : {
         "@type" : [
            "statistic",
            "Entity"
         ],
         "equivalentThreshold" : [
            "niiri:extent_threshold_id_2",
            "niiri:extent_threshold_id_3"
         ],
         "@id" : "niiri:extent_threshold_id",
         "clusterSizeInResels" : "0.0",
         "clusterSizeInVoxels" : "0",
         "rdfs:label" : "Extent Threshold: k>=0"
      },
      "MaskMap" : {
         "@type" : "Entity",
         "inCoordinateSpace" : "niiri:coordinate_space_id_1",
         "rdfs:label" : "Mask",
         "@id" : "niiri:mask_id_1",
         "wasDerivedFrom" : "niiri:mask_id_1_der",
         "location" : "Mask.nii.gz",
         "dct:format" : "image/nifti",
         "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#sha512" : "932fd9f0d55e9822748f4a9b35a0a7f0fe442f3e061e2eda48c2617a2938df50ea84deca8de0725641a0105b712a80a0c8931df9bdf3bef788b1041379d00875",
         "wasGeneratedBy" : "niiri:model_pe_id",
         "nidm:NIDM_0000106" : false,
         "nfo:fileName" : "Mask.nii.gz"
      },
      "Generation" : {
         "activity" : "niiri:export_id",
         "atTime" : "2014-05-19T10:30:00+01:00",
         "@id" : "_:f1b4bd76338a04597b3f698e59f695e53b1"
      },
      "Collection" : {
         "hasMRIProtocol" : "http://uri.neuinfo.org/nif/nifstd/birnlex_2250",
         "@id" : "niiri:data_id",
         "targetIntensity" : "100.0",
         "wasAttributedTo" : [
            "niiri:subject_id",
            "niiri:mr_scanner_id"
         ],
         "rdfs:label" : "Data",
         "nidm:NIDM_0000096" : true,
         "@type" : [
            "Data",
            "Entity"
         ]
      },
      "Coordinate" : [
         {
            "@type" : [
               "Location",
               "Entity"
            ],
            "nidm:NIDM_0000086" : "[ 45, -40, 32 ]",
            "@id" : "niiri:coordinate_0009",
            "rdfs:label" : "Coordinate: 0009"
         },
         {
            "nidm:NIDM_0000086" : "[ 60, -22, 11 ]",
            "@type" : [
               "Location",
               "Entity"
            ],
            "rdfs:label" : "Coordinate: 0005",
            "@id" : "niiri:coordinate_0005"
         },
         {
            "@type" : [
               "Location",
               "Entity"
            ],
            "nidm:NIDM_0000086" : "[ -60, -25, 11 ]",
            "@id" : "niiri:coordinate_0001",
            "rdfs:label" : "Coordinate: 0001"
         },
         {
            "nidm:NIDM_0000086" : "[ 63, -13, -4 ]",
            "@type" : [
               "Location",
               "Entity"
            ],
            "rdfs:label" : "Coordinate: 0004",
            "@id" : "niiri:coordinate_0004"
         },
         {
            "@id" : "niiri:coordinate_0003",
            "rdfs:label" : "Coordinate: 0003",
            "@type" : [
               "Location",
               "Entity"
            ],
            "nidm:NIDM_0000086" : "[ -66, -31, -1 ]"
         }
      ]
   },
   "@id" : "https://raw.githubusercontent.com/incf-nidash/nidm-specs/master/nidm/nidm-results/spm/example001/example001_spm_results.ttl",
   "@context" : "https://raw.githubusercontent.com/satra/nidm-jsonld/master/nidm-results.jsonld"
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
