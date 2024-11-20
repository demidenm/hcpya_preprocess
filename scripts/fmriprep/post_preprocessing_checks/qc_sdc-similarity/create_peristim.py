import warnings
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", 
                        message="A NumPy version >=1.18.5 and <1.25.0 is required for this version of SciPy")
import os
import argparse
import nibabel as nib
from glob import glob
import numpy as np
import os
from pyrelimri import masked_timeseries
from glob import glob
import matplotlib
matplotlib.use('Agg')

# sort paths
def get_run_sort(filepath):
    import re
    match = re.search(r'run-(\d+)', filepath)
    return int(match.group(1)) if match else float('inf')

# input arguments
parser = argparse.ArgumentParser(description="Script to run similarity estimate between func/anat masks")
parser.add_argument("--in_dir", help="directory with subjects data to BOLD and sourcedata path to events")
parser.add_argument("--sub_id", help="subject ID, without prefix 'sub-'")
parser.add_argument("--task", help="task label. In HCP using 'motor'", default='motor')
parser.add_argument("--roi_mask", help="path to ROI mask, in HCP using left visual [-6,-90,-2] from Neurosynth")
parser.add_argument("--out_path", help="Path to save peristimulus plots and data for subjects. Default = None", default=None)
# parse input args
args = parser.parse_args()
sub = args.sub_id
input_dir = args.in_dir
task = args.task
roimask = args.roi_mask
savedir = args.out_path

# Specs for running each step and labels from events files
scan_tr=.720
volumes=284
ses = '3T'
fwhm=4
sphere=8
filter_freq = 90
tr_delay=24
onsetcol = 'onset'
trialcol = 'trial_type'
conditioncol=['cue']

# paths,files,sort
inp_eventfiles = glob(f'{input_dir}/sub-{sub}/ses-{ses}/func/sub-{sub}_ses-{ses}_task-{task}_dir-*_run-*_events.tsv')
inp_boldfiles = glob(f'{input_dir}/sub-{sub}/ses-{ses}/func/sub-{sub}_ses-{ses}_task-{task}_dir-*_run-*_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz')
eventpaths_sortedrun = sorted(inp_eventfiles, key=get_run_sort)
boldpaths_sortedrun = sorted(inp_boldfiles, key=get_run_sort)

assert len(eventpaths_sortedrun) == len(boldpaths_sortedrun), f"Events {len(eventpaths_sortedrun)} & BOLD {len(boldpaths_sortedrun)} length dont match"

# extract timeseries
timeseries, sub_in = masked_timeseries.extract_time_series(bold_paths=boldpaths_sortedrun, roi_type='mask', roi_mask=roimask, 
                                                           radius_mm=sphere, fwhm_smooth=fwhm, high_pass_sec=filter_freq, detrend=True)

# lock to events
out_df = masked_timeseries.extract_postcue_trs_for_conditions(events_data=eventpaths_sortedrun, onset=onsetcol, 
                                                              trial_name=trialcol, bold_tr=scan_tr, bold_vols=volumes, time_series=timeseries, 
                                                              conditions=conditioncol, tr_delay=tr_delay, list_trpaths=sub_in)

masked_timeseries.plot_responses(df=out_df, tr=scan_tr, delay=tr_delay, style= 'white', save_path = f'{savedir}/{sub}_ses-{ses}_task-{task}_plot-peristim.png', show_plot=False, ylim = (-2, 2))

# save df and extract values
out_df.to_csv(f'{savedir}/{sub}_ses-{ses}_task-{task}_timeseries-roi.tsv', sep = '\t')
summary_df = out_df.groupby(['TR', 'Cue']).agg(
    Mean_Signal=('Mean_Signal', 'mean'),
    SE_Signal=('Mean_Signal', lambda x: x.std() / (len(x)**0.5))
).reset_index()

max_mean_signal_row = summary_df[0:16].loc[summary_df['Mean_Signal'].idxmax()]
peak_tr = max_mean_signal_row[0]
max_sig_tr = max_mean_signal_row[2]
se_sig_tr = max_mean_signal_row[3]
peak_tr, np.round(max_sig_tr,3), np.round(se_sig_tr,3)

print(peak_tr, max_sig_tr, se_sig_tr)
