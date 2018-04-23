# emacs: -*- mode: python-mode; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Test FSL Feat extractor"""


from datalad.api import Dataset
from datalad.api import create
from datalad.api import aggregate_metadata
from datalad.api import metadata
from datalad.tests.utils import with_tempfile
from datalad.tests.utils import with_tree
from datalad.tests.utils import ok_clean_git
from datalad.tests.utils import assert_status
from datalad.tests.utils import assert_result_count
from datalad.tests.utils import eq_
from datalad.tests.utils import assert_dict_equal
from datalad.tests.utils import assert_in
from datalad.tests.utils import assert_not_in

# dump of a real 1st-level design.fsf file
designfsf = """\
# FEAT version number
set fmri(version) 6.00

# Are we in MELODIC?
set fmri(inmelodic) 0

# Analysis level
# 1 : First-level analysis
# 2 : Higher-level analysis
set fmri(level) 1

# Which stages to run
# 0 : No first-level analysis (registration and/or group stats only)
# 7 : Full first-level analysis
# 1 : Pre-processing
# 2 : Statistics
set fmri(analysis) 7

# Use relative filenames
set fmri(relative_yn) 0

# Balloon help
set fmri(help_yn) 1

# Run Featwatcher
set fmri(featwatcher_yn) 0

# Cleanup first-level standard-space images
set fmri(sscleanup_yn) 0

# Output directory
set fmri(outputdir) "/tmp/tmp.U5HOVWLTMP/localizerdemo/1stlvl_glm"

# TR(s)
set fmri(tr) 2.000001 

# Total volumes
set fmri(npts) 156

# Delete volumes
set fmri(ndelete) 0

# Perfusion tag/control order
set fmri(tagfirst) 1

# Number of first-level analyses
set fmri(multiple) 1

# Higher-level input type
# 1 : Inputs are lower-level FEAT directories
# 2 : Inputs are cope images from FEAT directories
set fmri(inputtype) 2

# Carry out pre-stats processing?
set fmri(filtering_yn) 1

# Brain/background threshold, %
set fmri(brain_thresh) 10

# Critical z for design efficiency calculation
set fmri(critical_z) 5.3

# Noise level
set fmri(noise) 0.66

# Noise AR(1)
set fmri(noisear) 0.34

# Motion correction
# 0 : None
# 1 : MCFLIRT
set fmri(mc) 1

# Spin-history (currently obsolete)
set fmri(sh_yn) 0

# B0 fieldmap unwarping?
set fmri(regunwarp_yn) 0

# EPI dwell time (ms)
set fmri(dwell) 0.7

# EPI TE (ms)
set fmri(te) 35

# % Signal loss threshold
set fmri(signallossthresh) 10

# Unwarp direction
set fmri(unwarp_dir) y-

# Slice timing correction
# 0 : None
# 1 : Regular up (0, 1, 2, 3, ...)
# 2 : Regular down
# 3 : Use slice order file
# 4 : Use slice timings file
# 5 : Interleaved (0, 2, 4 ... 1, 3, 5 ... )
set fmri(st) 1

# Slice timings file
set fmri(st_file) ""

# BET brain extraction
set fmri(bet_yn) 1

# Spatial smoothing FWHM (mm)
set fmri(smooth) 5

# Intensity normalization
set fmri(norm_yn) 0

# Perfusion subtraction
set fmri(perfsub_yn) 0

# Highpass temporal filtering
set fmri(temphp_yn) 1

# Lowpass temporal filtering
set fmri(templp_yn) 0

# MELODIC ICA data exploration
set fmri(melodic_yn) 0

# Carry out main stats?
set fmri(stats_yn) 1

# Carry out prewhitening?
set fmri(prewhiten_yn) 1

# Add motion parameters to model
# 0 : No
# 1 : Yes
set fmri(motionevs) 1
set fmri(motionevsbeta) ""
set fmri(scriptevsbeta) ""

# Robust outlier detection in FLAME?
set fmri(robust_yn) 0

# Higher-level modelling
# 3 : Fixed effects
# 0 : Mixed Effects: Simple OLS
# 2 : Mixed Effects: FLAME 1
# 1 : Mixed Effects: FLAME 1+2
set fmri(mixed_yn) 2

# Number of EVs
set fmri(evs_orig) 6
set fmri(evs_real) 12
set fmri(evs_vox) 0

# Number of contrasts
set fmri(ncon_orig) 1
set fmri(ncon_real) 1

# Number of F-tests
set fmri(nftests_orig) 0
set fmri(nftests_real) 0

# Add constant column to design matrix? (obsolete)
set fmri(constcol) 0

# Carry out post-stats steps?
set fmri(poststats_yn) 1

# Pre-threshold masking?
set fmri(threshmask) ""

# Thresholding
# 0 : None
# 1 : Uncorrected
# 2 : Voxel
# 3 : Cluster
set fmri(thresh) 3

# P threshold
set fmri(prob_thresh) 0.05

# Z threshold
set fmri(z_thresh) 2.3

# Z min/max for colour rendering
# 0 : Use actual Z min/max
# 1 : Use preset Z min/max
set fmri(zdisplay) 0

# Z min in colour rendering
set fmri(zmin) 2

# Z max in colour rendering
set fmri(zmax) 8

# Colour rendering type
# 0 : Solid blobs
# 1 : Transparent blobs
set fmri(rendertype) 1

# Background image for higher-level stats overlays
# 1 : Mean highres
# 2 : First highres
# 3 : Mean functional
# 4 : First functional
# 5 : Standard space template
set fmri(bgimage) 1

# Create time series plots
set fmri(tsplot_yn) 1

# Registration to initial structural
set fmri(reginitial_highres_yn) 0

# Search space for registration to initial structural
# 0   : No search
# 90  : Normal search
# 180 : Full search
set fmri(reginitial_highres_search) 90

# Degrees of Freedom for registration to initial structural
set fmri(reginitial_highres_dof) 3

# Registration to main structural
set fmri(reghighres_yn) 0

# Search space for registration to main structural
# 0   : No search
# 90  : Normal search
# 180 : Full search
set fmri(reghighres_search) 90

# Degrees of Freedom for registration to main structural
set fmri(reghighres_dof) BBR

# Registration to standard image?
set fmri(regstandard_yn) 0

# Use alternate reference images?
set fmri(alternateReference_yn) 0

# Standard image
set fmri(regstandard) "/usr/share/fsl/5.0/data/standard/MNI152_T1_2mm_brain"

# Search space for registration to standard space
# 0   : No search
# 90  : Normal search
# 180 : Full search
set fmri(regstandard_search) 90

# Degrees of Freedom for registration to standard space
set fmri(regstandard_dof) 12

# Do nonlinear registration from structural to standard space?
set fmri(regstandard_nonlinear_yn) 0

# Control nonlinear warp field resolution
set fmri(regstandard_nonlinear_warpres) 10 

# High pass filter cutoff
set fmri(paradigm_hp) 80.0

# Total voxels
set fmri(totalVoxels) 34944000


# Number of lower-level copes feeding into higher-level analysis
set fmri(ncopeinputs) 0

# 4D AVW data or FEAT directory (1)
set feat_files(1) "/tmp/tmp.U5HOVWLTMP/localizerdemo/sub-02/dicoms_func_task-oneback_run-1_20140425155335_401"

# Add confound EVs text file
set fmri(confoundevs) 0

# EV 1 title
set fmri(evtitle1) "face"

# Basic waveform shape (EV 1)
# 0 : Square
# 1 : Sinusoid
# 2 : Custom (1 entry per volume)
# 3 : Custom (3 column format)
# 4 : Interaction
# 10 : Empty (all zeros)
set fmri(shape1) 3

# Convolution (EV 1)
# 0 : None
# 1 : Gaussian
# 2 : Gamma
# 3 : Double-Gamma HRF
# 4 : Gamma basis functions
# 5 : Sine basis functions
# 6 : FIR basis functions
set fmri(convolve1) 3

# Convolve phase (EV 1)
set fmri(convolve_phase1) 0

# Apply temporal filtering (EV 1)
set fmri(tempfilt_yn1) 1

# Add temporal derivative (EV 1)
set fmri(deriv_yn1) 1

# Custom EV file (EV 1)
set fmri(custom1) "/tmp/tmp.U5HOVWLTMP/localizerdemo/sub-02/onsets/run-1/face.txt"

# Orthogonalise EV 1 wrt EV 0
set fmri(ortho1.0) 0

# Orthogonalise EV 1 wrt EV 1
set fmri(ortho1.1) 0

# Orthogonalise EV 1 wrt EV 2
set fmri(ortho1.2) 0

# Orthogonalise EV 1 wrt EV 3
set fmri(ortho1.3) 0

# Orthogonalise EV 1 wrt EV 4
set fmri(ortho1.4) 0

# Orthogonalise EV 1 wrt EV 5
set fmri(ortho1.5) 0

# Orthogonalise EV 1 wrt EV 6
set fmri(ortho1.6) 0

# EV 2 title
set fmri(evtitle2) "house"

# Basic waveform shape (EV 2)
# 0 : Square
# 1 : Sinusoid
# 2 : Custom (1 entry per volume)
# 3 : Custom (3 column format)
# 4 : Interaction
# 10 : Empty (all zeros)
set fmri(shape2) 3

# Convolution (EV 2)
# 0 : None
# 1 : Gaussian
# 2 : Gamma
# 3 : Double-Gamma HRF
# 4 : Gamma basis functions
# 5 : Sine basis functions
# 6 : FIR basis functions
set fmri(convolve2) 3

# Convolve phase (EV 2)
set fmri(convolve_phase2) 0

# Apply temporal filtering (EV 2)
set fmri(tempfilt_yn2) 1

# Add temporal derivative (EV 2)
set fmri(deriv_yn2) 1

# Custom EV file (EV 2)
set fmri(custom2) "/tmp/tmp.U5HOVWLTMP/localizerdemo/sub-02/onsets/run-1/house.txt"

# Orthogonalise EV 2 wrt EV 0
set fmri(ortho2.0) 0

# Orthogonalise EV 2 wrt EV 1
set fmri(ortho2.1) 0

# Orthogonalise EV 2 wrt EV 2
set fmri(ortho2.2) 0

# Orthogonalise EV 2 wrt EV 3
set fmri(ortho2.3) 0

# Orthogonalise EV 2 wrt EV 4
set fmri(ortho2.4) 0

# Orthogonalise EV 2 wrt EV 5
set fmri(ortho2.5) 0

# Orthogonalise EV 2 wrt EV 6
set fmri(ortho2.6) 0

# EV 3 title
set fmri(evtitle3) "body"

# Basic waveform shape (EV 3)
# 0 : Square
# 1 : Sinusoid
# 2 : Custom (1 entry per volume)
# 3 : Custom (3 column format)
# 4 : Interaction
# 10 : Empty (all zeros)
set fmri(shape3) 3

# Convolution (EV 3)
# 0 : None
# 1 : Gaussian
# 2 : Gamma
# 3 : Double-Gamma HRF
# 4 : Gamma basis functions
# 5 : Sine basis functions
# 6 : FIR basis functions
set fmri(convolve3) 3

# Convolve phase (EV 3)
set fmri(convolve_phase3) 0

# Apply temporal filtering (EV 3)
set fmri(tempfilt_yn3) 1

# Add temporal derivative (EV 3)
set fmri(deriv_yn3) 1

# Custom EV file (EV 3)
set fmri(custom3) "/tmp/tmp.U5HOVWLTMP/localizerdemo/sub-02/onsets/run-1/body.txt"

# Orthogonalise EV 3 wrt EV 0
set fmri(ortho3.0) 0

# Orthogonalise EV 3 wrt EV 1
set fmri(ortho3.1) 0

# Orthogonalise EV 3 wrt EV 2
set fmri(ortho3.2) 0

# Orthogonalise EV 3 wrt EV 3
set fmri(ortho3.3) 0

# Orthogonalise EV 3 wrt EV 4
set fmri(ortho3.4) 0

# Orthogonalise EV 3 wrt EV 5
set fmri(ortho3.5) 0

# Orthogonalise EV 3 wrt EV 6
set fmri(ortho3.6) 0

# EV 4 title
set fmri(evtitle4) "object"

# Basic waveform shape (EV 4)
# 0 : Square
# 1 : Sinusoid
# 2 : Custom (1 entry per volume)
# 3 : Custom (3 column format)
# 4 : Interaction
# 10 : Empty (all zeros)
set fmri(shape4) 3

# Convolution (EV 4)
# 0 : None
# 1 : Gaussian
# 2 : Gamma
# 3 : Double-Gamma HRF
# 4 : Gamma basis functions
# 5 : Sine basis functions
# 6 : FIR basis functions
set fmri(convolve4) 2

# Convolve phase (EV 4)
set fmri(convolve_phase4) 0

# Apply temporal filtering (EV 4)
set fmri(tempfilt_yn4) 1

# Add temporal derivative (EV 4)
set fmri(deriv_yn4) 1

# Custom EV file (EV 4)
set fmri(custom4) "/tmp/tmp.U5HOVWLTMP/localizerdemo/sub-02/onsets/run-1/object.txt"

# Gamma sigma (EV 4)
set fmri(gammasigma4) 3

# Gamma delay (EV 4)
set fmri(gammadelay4) 6

# Orthogonalise EV 4 wrt EV 0
set fmri(ortho4.0) 0

# Orthogonalise EV 4 wrt EV 1
set fmri(ortho4.1) 0

# Orthogonalise EV 4 wrt EV 2
set fmri(ortho4.2) 0

# Orthogonalise EV 4 wrt EV 3
set fmri(ortho4.3) 0

# Orthogonalise EV 4 wrt EV 4
set fmri(ortho4.4) 0

# Orthogonalise EV 4 wrt EV 5
set fmri(ortho4.5) 0

# Orthogonalise EV 4 wrt EV 6
set fmri(ortho4.6) 0

# EV 5 title
set fmri(evtitle5) "scene"

# Basic waveform shape (EV 5)
# 0 : Square
# 1 : Sinusoid
# 2 : Custom (1 entry per volume)
# 3 : Custom (3 column format)
# 4 : Interaction
# 10 : Empty (all zeros)
set fmri(shape5) 3

# Convolution (EV 5)
# 0 : None
# 1 : Gaussian
# 2 : Gamma
# 3 : Double-Gamma HRF
# 4 : Gamma basis functions
# 5 : Sine basis functions
# 6 : FIR basis functions
set fmri(convolve5) 3

# Convolve phase (EV 5)
set fmri(convolve_phase5) 0

# Apply temporal filtering (EV 5)
set fmri(tempfilt_yn5) 1

# Add temporal derivative (EV 5)
set fmri(deriv_yn5) 1

# Custom EV file (EV 5)
set fmri(custom5) "/tmp/tmp.U5HOVWLTMP/localizerdemo/sub-02/onsets/run-1/scene.txt"

# Orthogonalise EV 5 wrt EV 0
set fmri(ortho5.0) 0

# Orthogonalise EV 5 wrt EV 1
set fmri(ortho5.1) 0

# Orthogonalise EV 5 wrt EV 2
set fmri(ortho5.2) 0

# Orthogonalise EV 5 wrt EV 3
set fmri(ortho5.3) 0

# Orthogonalise EV 5 wrt EV 4
set fmri(ortho5.4) 0

# Orthogonalise EV 5 wrt EV 5
set fmri(ortho5.5) 0

# Orthogonalise EV 5 wrt EV 6
set fmri(ortho5.6) 0

# EV 6 title
set fmri(evtitle6) "scramble"

# Basic waveform shape (EV 6)
# 0 : Square
# 1 : Sinusoid
# 2 : Custom (1 entry per volume)
# 3 : Custom (3 column format)
# 4 : Interaction
# 10 : Empty (all zeros)
set fmri(shape6) 3

# Convolution (EV 6)
# 0 : None
# 1 : Gaussian
# 2 : Gamma
# 3 : Double-Gamma HRF
# 4 : Gamma basis functions
# 5 : Sine basis functions
# 6 : FIR basis functions
set fmri(convolve6) 3

# Convolve phase (EV 6)
set fmri(convolve_phase6) 0

# Apply temporal filtering (EV 6)
set fmri(tempfilt_yn6) 1

# Add temporal derivative (EV 6)
set fmri(deriv_yn6) 1

# Custom EV file (EV 6)
set fmri(custom6) "/tmp/tmp.U5HOVWLTMP/localizerdemo/sub-02/onsets/run-1/scramble.txt"

# Orthogonalise EV 6 wrt EV 0
set fmri(ortho6.0) 0

# Orthogonalise EV 6 wrt EV 1
set fmri(ortho6.1) 0

# Orthogonalise EV 6 wrt EV 2
set fmri(ortho6.2) 0

# Orthogonalise EV 6 wrt EV 3
set fmri(ortho6.3) 0

# Orthogonalise EV 6 wrt EV 4
set fmri(ortho6.4) 0

# Orthogonalise EV 6 wrt EV 5
set fmri(ortho6.5) 0

# Orthogonalise EV 6 wrt EV 6
set fmri(ortho6.6) 0

# Contrast & F-tests mode
# real : control real EVs
# orig : control original EVs
set fmri(con_mode_old) orig
set fmri(con_mode) orig

# Display images for contrast_real 1
set fmri(conpic_real.1) 1

# Title for contrast_real 1
set fmri(conname_real.1) "FFA"

# Real contrast_real vector 1 element 1
set fmri(con_real1.1) 2.0

# Real contrast_real vector 1 element 2
set fmri(con_real1.2) 0

# Real contrast_real vector 1 element 3
set fmri(con_real1.3) -1.0

# Real contrast_real vector 1 element 4
set fmri(con_real1.4) 0

# Real contrast_real vector 1 element 5
set fmri(con_real1.5) 0.0

# Real contrast_real vector 1 element 6
set fmri(con_real1.6) 0

# Real contrast_real vector 1 element 7
set fmri(con_real1.7) 0.0

# Real contrast_real vector 1 element 8
set fmri(con_real1.8) 0

# Real contrast_real vector 1 element 9
set fmri(con_real1.9) -1.0

# Real contrast_real vector 1 element 10
set fmri(con_real1.10) 0

# Real contrast_real vector 1 element 11
set fmri(con_real1.11) 0

# Real contrast_real vector 1 element 12
set fmri(con_real1.12) 0

# Display images for contrast_orig 1
set fmri(conpic_orig.1) 1

# Title for contrast_orig 1
set fmri(conname_orig.1) "FFA"

# Real contrast_orig vector 1 element 1
set fmri(con_orig1.1) 2.0

# Real contrast_orig vector 1 element 2
set fmri(con_orig1.2) -1.0

# Real contrast_orig vector 1 element 3
set fmri(con_orig1.3) 0.0

# Real contrast_orig vector 1 element 4
set fmri(con_orig1.4) 0.0

# Real contrast_orig vector 1 element 5
set fmri(con_orig1.5) -1.0

# Real contrast_orig vector 1 element 6
set fmri(con_orig1.6) 0

# Contrast masking - use >0 instead of thresholding?
set fmri(conmask_zerothresh_yn) 0

# Do contrast masking at all?
set fmri(conmask1_1) 0

##########################################################
# Now options that don't appear in the GUI

# Alternative (to BETting) mask image
set fmri(alternative_mask) ""

# Initial structural space registration initialisation transform
set fmri(init_initial_highres) ""

# Structural space registration initialisation transform
set fmri(init_highres) ""

# Standard space registration initialisation transform
set fmri(init_standard) ""

# For full FEAT analysis: overwrite existing .feat output dir?
set fmri(overwrite_yn) 0
"""

# dump of a real cluster_zstat?.txt file
clusterzstat = """\
Cluster Index	Voxels	P	-log10(P)	Z-MAX	Z-MAX X (vox)	Z-MAX Y (vox)	Z-MAX Z (vox)	Z-COG X (vox)	Z-COG Y (vox)	Z-COG Z (vox)	COPE-MAX	COPE-MAX X (vox)	COPE-MAX Y (vox)	COPE-MAX Z (vox)	COPE-MEAN
7	347	1.97e-09	8.71	11.9	26	19	7	23.9	18.6	8.69	666	25	20	7	171
6	164	4.05e-05	4.39	4.91	55	16	24	53.5	14.2	22.8	284	55	15	22	98.2
5	85	0.00926	2.03	4.89	30	49	21	32	49.3	19.8	143	35	48	18	71.6
4	75	0.0203	1.69	4	27	13	23	21.3	19.3	22.5	170	21	17	20	74.4
3	65	0.0459	1.34	4.8	22	42	24	19.3	43.9	20.9	248	22	42	24	82.3
2	64	0.0499	1.3	9.85	51	19	5	51.4	18.5	5.31	529	51	20	6	191
1	64	0.0499	1.3	6.2	39	5	7	38.8	6.26	9.36	427	39	5	7	162
"""


@with_tree(tree={
    '.datalad': {
        'config': '[datalad "metadata"]\n  nativetype = fslfeat'
    },
    'some': {
        'sub-02.feat': {
            'design.fsf': designfsf,
            'cluster_zstat1.txt': clusterzstat,
            # TODO can be more than one (one per contrast)
        }
    }
})
def test_metadata_from_1stlvl(path):
    ds = Dataset(path).create(force=True)
    ds.add('.')
    ds.aggregate_metadata()
    ok_clean_git(ds.path)
    res = ds.metadata(reporton='datasets')
    assert_result_count(res, 1)
    meta = res[0]['metadata']['fslfeat']
    eq_(len(meta['analysis']), 1)
    anameta = meta['analysis'][0]
    eq_(len(anameta['ev']), 6)
    eq_(len(anameta['contrasts']), 1)
    for con in anameta['contrasts']:
        assert_in('name', con)
        assert_in('clusters', con)
        eq_(len(con['clusters']), 7)
