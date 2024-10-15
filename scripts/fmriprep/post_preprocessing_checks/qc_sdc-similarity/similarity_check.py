import warnings
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", 
                        message="A NumPy version >=1.18.5 and <1.25.0 is required for this version of SciPy")
import os
import fnmatch
import argparse
import nibabel as nib
from glob import glob
from nilearn.image import resample_img
from nipype.interfaces import fsl
from pyrelimri import similarity

# input arguments
parser = argparse.ArgumentParser(description="Script to run similarity estimate between func/anat masks")
parser.add_argument("--in_dat", help="path to subjects session subfolders")
parser.add_argument("--task", help="task label")
parser.add_argument("--run", help="task label", default=None)
parser.add_argument("--stype", help="similarity type, dice or jaccard")

# parse input args
args = parser.parse_args()
input_dir = args.in_dat
task = args.task
run = args.run
stype = args.stype

# folder paths
anat_dir = f'{input_dir}/anat'
func_dir = f'{input_dir}/func'
fmap_dir = f'{input_dir}/fmap'
fsl_out = f'{input_dir}/anat/fsl'

# glob files to set variables 
anat_file = glob(f'{anat_dir}/*_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz')[0]

# dont want to run on MNI but subject space, ignore MNI
all_files = glob(f'{anat_dir}/*.nii.gz')
filtered_files = [file for file in all_files if not fnmatch.fnmatch(file, '*space-MNI152*')]

# Check if any files are left after filtering
if filtered_files:
    # Use the filtered files as needed
    fp_gm = next((file for file in filtered_files if '_label-GM_probseg.nii.gz' in file), None)
    fp_wm = next((file for file in filtered_files if '_label-WM_probseg.nii.gz' in file), None)
    fp_csf = next((file for file in filtered_files if '_label-CSF_probseg.nii.gz' in file), None)
    t1w_file = next((file for file in filtered_files if '_T1w.nii.gz' in file), None)
    brainmask_file = next((file for file in filtered_files if '-brain_mask.nii.gz' in file), None)

# set bold and anat files
if run is None:
    bold_file = glob(f'{func_dir}/*_task-{task}_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz')[0]
else:
    bold_file = glob(f'{func_dir}/*_task-{task}_run-{run}_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz')[0]

# Create bet output name
t1w_base = os.path.basename(t1w_file)
prefix_t1w = t1w_base.rsplit('.', 2)[0]
t1w_brain_fname = f'{fsl_out}/{prefix_t1w}-brain.nii.gz'

#create fs output img, reshape/mod affine
fs_resampled = f'{anat_dir}/fs_resampled.nii.gz'

if not os.path.exists(fs_resampled):
    brain_mask = nib.load(brainmask_file)
    fs_brain = nib.load(f'{anat_dir}/fs_brain.nii.gz')
    
    mask_affine = brain_mask.affine
    mask_shape = brain_mask.shape
    fs_resample = resample_img(img=fs_brain, 
                               target_affine=mask_affine, target_shape=mask_shape)
    nib.save(fs_resample, fs_resampled)

if not os.path.exists(fsl_out):
    try:
        # Create the fsl output directory if it doesn't exist
        os.makedirs(fsl_out)
        
        # Run BET
        bet_run = fsl.BET()
        bet_run.inputs.in_file = t1w_file
        bet_run.inputs.reduce_bias = True
        #bet_run.inputs.robust = True
        bet_run.inputs.out_file = t1w_brain_fname
        bet_out = bet_run.run()
        # Run FAST
        fast_run = fsl.FAST()
        fast_run.inputs.in_files = t1w_brain_fname
        # fast_run.inputs.out_basename = t1w_brain_fname
        fast_out = fast_run.run()
    except Exception as e:
        # exception 
        print(f"An error occurred: {e}")

# sets CSF [0], GM [1], WM [2]
orig_csf = glob(f'{fsl_out}/*_T1w-brain_pve_0.nii.gz')[0]
orig_gm = glob(f'{fsl_out}/*_T1w-brain_pve_1.nii.gz')[0]
orig_wm = glob(f'{fsl_out}/*_T1w-brain_pve_2.nii.gz')[0]

# run similarity
sim_fs_check = similarity.image_similarity(imgfile1=brainmask_file,
                                           imgfile2=fs_resampled,
                                           similarity_type=stype)

sim_anatfunc = similarity.image_similarity(imgfile1=anat_file,
                                           imgfile2=bold_file,
                                           similarity_type=stype)

origcsf_fpcsf = similarity.image_similarity(imgfile1=orig_csf,
                                            imgfile2=fp_csf,
                                            similarity_type=stype)

origwm_fpwm = similarity.image_similarity(imgfile1=orig_wm,
                                          imgfile2=fp_wm,
                                          similarity_type=stype)

origgm_fpgm = similarity.image_similarity(imgfile1=orig_gm,
                                          imgfile2=fp_gm,
                                          similarity_type=stype)


print(round(sim_fs_check, 2), round(sim_anatfunc, 2), round(origcsf_fpcsf, 2), 
      round(origwm_fpwm, 2), round(origgm_fpgm, 2))
