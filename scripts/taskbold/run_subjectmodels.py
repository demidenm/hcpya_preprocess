import subprocess
import os
import argparse
import json
import pandas as pd
from pathlib import Path
from nilearn.glm.first_level import FirstLevelModel
from glm_utils import (est_contrast_vifs, generate_tablecontents, create_design_matrix, 
compute_save_contrasts, plot_design_vifs, visualize_contrastweights, compute_fixedeff)
from prep_eventsdata import (comb_names, prep_gamble_events, prep_motor_events, 
prep_social_events, prep_language_events, prep_relation_events, prep_emotion_events, prep_wm_events)
from bids.layout import parse_file_entities
import matplotlib.pyplot as plt
plt.switch_backend('Agg') # turn off back end display to create plots


def get_files(bash_command):
    command_out = subprocess.run(bash_command, shell=True, capture_output=True, text=True)
    files = [line.split()[-1] for line in command_out.stdout.strip().split("\n") if line]
    
    return files
    
def sync_matching_runs(subject_id, sesid, taskname, events_path, sync_destination):
    """
    Syncs the matching fMRIPrep bold, confounds and copying event files for a given task and subject.

    Parameters:
        subject_id (int): Subject ID
        ses (str): Session full string (e.g., ses-3T)
        task (str): Task name (e.g., motor)
        events_path (str): Path to local event files
        sync_to (str): Destination to copy matching files to for analyses
    
    Returns:
        Runs found (list) or 'None' (str)
    """

    # Get fMRIPrep bold files from S3
    # wm task, unlike others, is uppercase. However, events are not. Modify to account for upper /lower diff
    fmriprep_lab = taskname.upper() if taskname == "wm" else taskname

    fmriprep_boldlist = f"s3cmd ls --recursive s3://hcp-youth/derivatives/fmriprep_v24_0_1/{sesid}/{subject_id}/{sesid}/func/ | grep 'task-{fmriprep_lab}_dir.*_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz'"
    bold_files = get_files(fmriprep_boldlist)
    print(bold_files)

    confounds_list = f"s3cmd ls --recursive s3://hcp-youth/derivatives/fmriprep_v24_0_1/{sesid}/{subject_id}/{sesid}/func/ | grep 'task-{fmriprep_lab}_dir.*_desc-confounds_timeseries.tsv'"
    confounds_files = get_files(confounds_list)

    # get events list
    events_list = f"ls {events_path}/{subject_id}/{ses}/func/ | grep 'task-{taskname}.*_events.tsv'"
    event_files = get_files(events_list)

    # task and run consistency
    matched_runs = {}
    for bold_file in bold_files:
        bold_metadata = parse_file_entities(bold_file)
        bold_task = bold_metadata.get("task")
        bold_run = bold_metadata.get("run")

        # Find the corresponding confounds file
        confound_file = next((cf for cf in confounds_files if f"run-{bold_run}" in cf), None)

        for event_file in event_files:
            event_metadata = parse_file_entities(event_file)
            event_task = event_metadata.get("task")
            event_run = event_metadata.get("run")

            if bold_task == event_task and bold_run == event_run and confound_file:
                matched_runs[bold_run] = (bold_file, confound_file, event_file)

    # Sync only matching runs
    if not matched_runs:
        return [], None, None

    sync_commands = []
    for run, (bold_file, confound_file, event_file) in matched_runs.items():
        bold_sync_cmd = f"s3cmd get {bold_file} {sync_destination}/ --continue"
        confound_sync_cmd = f"s3cmd get {confound_file} {sync_destination}/ --continue"
        event_sync_cmd = f"cp {events_path}/{subject_id}/{ses}/func/{event_file} {sync_destination}/"

        subprocess.run(bold_sync_cmd, shell=True)
        subprocess.run(confound_sync_cmd, shell=True)
        subprocess.run(event_sync_cmd, shell=True)
        
        sync_commands.append((bold_sync_cmd, confound_sync_cmd, event_sync_cmd))

    return list(matched_runs.keys()), bold_task, event_task


# Parse command line arguments
parser = argparse.ArgumentParser(description='Download files from S3 bucket')
parser.add_argument('--subject', type=str, help='subject id, including prefix, e.g sub-01133')
parser.add_argument('--model', type=str, help='model type in config task file, e.g. hcp or alt')
parser.add_argument('--config', type=str, help='path to configuration file with task / model details')
parser.add_argument('--analysisout', type=str, help='Output folder for analyses')
parser.add_argument('--workdir', type=str, help='Working directory for copy and holidng events/bold files, default /tmp/', default="/tmp/")

args = parser.parse_args()

# Configuration from command line args
subj_id = args.subject
studydetails_path=args.config
modtype=args.model
output_folder = args.analysisout
working_folder = args.workdir

# set variables and paths
eventsdir = "/home/feczk001/mdemiden/data/hcp_events"
brain_mni_mask = "/home/feczk001/mdemiden/slurm_ABCD_s3/hcpya_preprocess/scripts/taskbold/masks/MNI152NLin2009cAsym_res-02_desc-brain_mask.nii.gz"
task_list = ['motor','gambling','language','social','wm','emotion', 'relational']
ses = "ses-3T"
firstlvl = f"{output_folder}/firstlvl/{subj_id}"
fixedeff = f"{output_folder}/fixedeff/{subj_id}"
os.makedirs(firstlvl, exist_ok=True)
os.makedirs(fixedeff, exist_ok=True)
os.makedirs(f"{firstlvl}/figures", exist_ok=True)

# task, model specs
with open(studydetails_path, 'r') as file:
    study_details = json.load(file)


for task in task_list:    
    print(f"Starting task: {task}")
    runs, bold_taskname, events_taskname = sync_matching_runs(subject_id=subj_id, sesid=ses, taskname=task, 
    events_path=eventsdir, sync_destination=working_folder)

    if not runs:
        print(f"No matching runs found for subject {subj_id} and task {task}")
        continue

    for run in runs:
        config = study_details[task]

        mod_spec = modtype
        mod_config = config[mod_spec]
        fwhm = float(config['fwhm'])
        ar_noisemod = str(config['noise_mod'])
        highpass = int(config['highpass']) if config['highpass'] else None
        detrend = str(config['detrend']) if config['detrend'] else None
        n_vols = int(config['num_volumes'])

        event_path = next(Path(working_folder).glob(f"{subj_id}_{ses}_task-{events_taskname}_dir-*_run-{run}_events.tsv"), None)
        event_df = pd.read_csv(event_path, sep = '\t')
        eventdf_cpy = event_df[event_df['trial_type'].isin(mod_config['trialtype_filter'])].copy()

        # conf files
        conf_fullpath = f"{subj_id}_{ses}_task-{bold_taskname}_dir-*_run-{run}_desc-confounds_timeseries.tsv"
        conf_path = next(Path(working_folder).glob(conf_fullpath), None)


        common_params = {
        'eventsdf': event_df, 
        'trialtype_colname': mod_config['trialtype_colname'],
        'incl_trialtypes': mod_config['trialtype_filter'],
        'modtype': mod_spec
        }
        # Process based on task type
        if task == 'motor':
            # Motor task doesn't use new_trialcol_name
            events_dat = prep_motor_events(**common_params)
        elif task == 'gambling':
            events_dat = prep_gamble_events(**common_params, new_trialcol_name='new_trialtype')
        elif task == 'language':
            events_dat = prep_language_events(**common_params, new_trialcol_name='new_trialtype')
        elif task == 'social':
            events_dat = prep_social_events(**common_params, new_trialcol_name='new_trialtype')
        elif task == 'wm':
            events_dat = prep_wm_events(**common_params, new_trialcol_name='new_trialtype')
        elif task == 'emotion':
            events_dat = prep_emotion_events(**common_params, new_trialcol_name='new_trialtype')
        elif task == 'relational':
            events_dat = prep_relation_events(**common_params, new_trialcol_name='new_trialtype')

        # Create the design matrix
        if task in ['gambling', 'social', 'wm']:
            design_matrix = create_design_matrix(
                eventdf=events_dat, conf_path=conf_path, 
                conflist_filt=mod_config['nusiance_regressors'], 
                stc=bool(config['slice_time_corr']), mod_dict=mod_config, 
                volumes=n_vols, time_rep=float(config['boldtr']), 
                hrf_type=config['hrf_type'], driftmod=detrend, 
                highpass=highpass, trialtype_colname='new_trialtype'
            )
        else:
            design_matrix = create_design_matrix(
                eventdf=events_dat, conf_path=conf_path, 
                conflist_filt=mod_config['nusiance_regressors'], 
                stc=bool(config['slice_time_corr']), mod_dict=mod_config, 
                volumes=n_vols, time_rep=float(config['boldtr']), 
                hrf_type=config['hrf_type'], driftmod=detrend, 
                highpass=highpass
            )
        # VIFs ESTIMATE WITH ALL TASK REGRESSORS
        filtered_columns = design_matrix.columns[~design_matrix.columns.str.contains(mod_config['nusiance_regressors'], regex=True)]
        reg_dict = {item: item for item in filtered_columns if item != "constant"}
        con_vifs = est_contrast_vifs(desmat=design_matrix, contrasts=mod_config['contrasts'])
        reg_vifs = est_contrast_vifs(desmat=design_matrix, contrasts=reg_dict)
        # create / save figures
        fig = plot_design_vifs(designmat=design_matrix, regressor_vifs=reg_vifs, contrast_vifs=con_vifs, task_name=task)
        save_desvifs = f"{firstlvl}/figures/{task}_design_vifs.png"
        fig.savefig(save_desvifs, dpi=300, bbox_inches='tight')
        plt.close()

        fig, _, _ = visualize_contrastweights(design_matrix=design_matrix, config_contrasts=mod_config['contrasts'], 
                                      nusiance_exclude=mod_config['nusiance_regressors'])
        save_con = f"{firstlvl}/figures/{task}_contrasts.png"
        fig.savefig(save_con, dpi=300, bbox_inches='tight')
        plt.close()

        # run FirstLevel
        bold_fullpath = f"{subj_id}_ses-3T_task-{bold_taskname}_dir-*_run-{run}_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz"
        bold_path = next(Path(working_folder).glob(bold_fullpath), None)

        # first lvl model & compute contrasts
        fmri_glm = FirstLevelModel(subject_label=subj_id, mask_img=brain_mni_mask,
                                    t_r=float(config['boldtr']), smoothing_fwhm=fwhm,
                                    standardize=False, noise_model=ar_noisemod, drift_model=detrend, high_pass=highpass)
        run_fmri_glm = fmri_glm.fit(bold_path, design_matrices=design_matrix)

        compute_save_contrasts(glm_res=run_fmri_glm, sess_lab=ses, condict=mod_config["contrasts"], outfold=firstlvl, 
                            subjid=subj_id, task=task, run=run)

    if len(runs) > 1:
        print("running fixed effects")
        compute_fixedeff(subjid=subj_id, task=task, sess_lab=ses, condict=mod_config["contrasts"], 
                 inpfold=firstlvl, outfold=fixedeff,prec_weight=True)
    else:
        print(f"{subj_id} for {task} contains <2 runs (e.g runs: {len(runs)})")


print("First Level and Fixed Effect Models successfully completed for:", subj_id)
