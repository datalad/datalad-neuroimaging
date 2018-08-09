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


# TODO update when format changes to a compacted JSON-LD form
example_metadata = """\
{
    "NIDMResultsExporter_type": "spm_results_nidm",
    "NIDMResultsExporter_softwareVersion": "12.7057",
    "NIDMResults_version": "1.3.0",
    "NeuroimagingAnalysisSoftware_type": "scr_SPM",
    "NeuroimagingAnalysisSoftware_label": "SPM",
    "NeuroimagingAnalysisSoftware_softwareVersion": "12.7219",
    "ImagingInstrument_type": "nlx_MagneticResonanceImagingScanner",
    "Data_grandMeanScaling": true,
    "Data_targetIntensity": 100,
    "Data_hasMRIProtocol": "nlx_FunctionalMRIProtocol",
    "ParameterEstimateMaps": [
        "/test/data/nidmresults-examples/spm_full_example001/beta_0001.nii",
        "/test/data/nidmresults-examples/spm_full_example001/beta_0002.nii"
    ],
    "ResidualMeanSquaresMap_atLocation": "/test/data/nidmresults-examples/spm_full_example001/ResMS.nii",
    "ReselsPerVoxelMap_atLocation": "/test/data/nidmresults-examples/spm_full_example001/RPV.nii",
    "Contrasts": {
        "StatisticMap_contrastName": "passive listening > rest",
        "ContrastWeightMatrix_value": [1,0],
        "StatisticMap_statisticType": "obo_TStatistic",
        "StatisticMap_errorDegreesOfFreedom": 83.9999999999599,
        "ContrastStandardErrorMap_atLocation": "/test/data/nidmresults-examples/spm_full_example001/oct-p80GGE/ContrastStandardError.nii.gz"
    },
    "ClusterDefinitionCriteria_hasConnectivityCriterion": "nidm_voxel18connected",
    "PeakDefinitionCriteria_minDistanceBetweenPeaks": 8,
    "PeakDefinitionCriteria_maxNumberOfPeaksPerCluster": 3,
    "Inferences": {
        "HeightThreshold_type": "obo_FWERAdjustedPValue",
        "HeightThreshold_value": 0.0499999999999976,
        "ExtentThreshold_type": "obo_Statistic",
        "ExtentThreshold_clusterSizeInVoxels": 0,
        "ExtentThreshold_clusterSizeInResels": 0,
        "HeightThreshold_equivalentThreshold": [
            {
                "HeightThreshold_type": "obo_Statistic",
                "HeightThreshold_value": 4.852417456895391
            },
            {
                "HeightThreshold_type": "nidm_PValueUncorrected",
                "HeightThreshold_value": 2.7772578456986e-06
            }
        ],
        "ExtentThreshold_equivalentThreshold": [
            {
                "ExtentThreshold_type": "obo_FWERAdjustedPValue",
                "ExtentThreshold_value": 1
            },
            {
                "ExtentThreshold_type": "nidm_PValueUncorrected",
                "ExtentThreshold_value": 1
            }
        ],
        "Inference_hasAlternativeHypothesis": "nidm_OneTailedTest",
        "StatisticMap_contrastName": ["passive listening > rest"],
        "ExcursionSetMap_atLocation": "/test/data/nidmresults-examples/spm_full_example001/oct-p80GGE/ExcursionSet.nii.gz",
        "ExcursionSetMap_numberOfSupraThresholdClusters": 5,
        "ExcursionSetMap_pValue": 2.835106815979316e-09,
        "ClusterLabelsMap_atLocation": "/test/data/nidmresults-examples/spm_full_example001/oct-p80GGE/ClusterLabels.nii.gz",
        "ExcursionSetMap_hasMaximumIntensityProjection": "/test/data/nidmresults-examples/spm_full_example001/oct-p80GGE/MaximumIntensityProjection.png",
        "Clusters": [
            {
                "SupraThresholdCluster_clusterSizeInVoxels": 839,
                "SupraThresholdCluster_clusterSizeInResels": 6.312656968091135,
                "SupraThresholdCluster_pValueUncorrected": 3.558968244804772e-19,
                "SupraThresholdCluster_pValueFWER": 0,
                "SupraThresholdCluster_qValueFDR": 1.779484122402386e-18,
                "Peaks": [
                    {
                        "Peak_value": 17.5207633972168,
                        "Coordinate_coordinateVector": [-60,-25,11],
                        "Peak_pValueUncorrected": 4.440892098500626e-16,
                        "Peak_equivalentZStatistic": null,
                        "Peak_pValueFWER": 0,
                        "Peak_qValueFDR": 1.191565917138381e-11
                    },
                    {
                        "Peak_value": 13.03214073181152,
                        "Coordinate_coordinateVector": [-42,-31,11],
                        "Peak_pValueUncorrected": 4.440892098500626e-16,
                        "Peak_equivalentZStatistic": null,
                        "Peak_pValueFWER": 0,
                        "Peak_qValueFDR": 1.191565917138381e-11
                    },
                    {
                        "Peak_value": 10.28560161590576,
                        "Coordinate_coordinateVector": [-66,-31,-1],
                        "Peak_pValueUncorrected": 4.440892098500626e-16,
                        "Peak_equivalentZStatistic": null,
                        "Peak_pValueFWER": 7.69451169446711e-12,
                        "Peak_qValueFDR": 6.841212602749916e-10
                    }
                ]
            },
            {
                "SupraThresholdCluster_clusterSizeInVoxels": 695,
                "SupraThresholdCluster_clusterSizeInResels": 5.229197369276923,
                "SupraThresholdCluster_pValueUncorrected": 5.342802826320728e-17,
                "SupraThresholdCluster_pValueFWER": 0,
                "SupraThresholdCluster_qValueFDR": 1.335700706580182e-16,
                "Peaks": [
                    {
                        "Peak_value": 13.54255771636963,
                        "Coordinate_coordinateVector": [63,-13,-4],
                        "Peak_pValueUncorrected": 4.440892098500626e-16,
                        "Peak_equivalentZStatistic": null,
                        "Peak_pValueFWER": 0,
                        "Peak_qValueFDR": 1.191565917138381e-11
                    },
                    {
                        "Peak_value": 12.47287178039551,
                        "Coordinate_coordinateVector": [60,-22,11],
                        "Peak_pValueUncorrected": 4.440892098500626e-16,
                        "Peak_equivalentZStatistic": null,
                        "Peak_pValueFWER": 0,
                        "Peak_qValueFDR": 1.191565917138381e-11
                    }
                ]
            }
        ]
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
        'Contrasts',
        res['metadata']['datalad_unique_content_properties']['nidmresults'])
