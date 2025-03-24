import subprocess
import os
import argparse
import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import date
from glm_utils import (est_contrast_vifs, generate_tablecontents, create_design_matrix, 
compute_save_contrasts, plot_design_vifs, visualize_contrastweights, compute_fixedeff, get_numvolumes, run_firstlvl_computecons, 
get_files, sync_matching_runs)
from prep_eventsdata import (comb_names, prep_gamble_events, prep_motor_events, 
prep_social_events, prep_language_events, prep_relation_events, prep_emotion_events, prep_wm_events)
from pyrelimri.similarity import image_similarity
plt.switch_backend('Agg') # turn off back end display to create plots


# Parse command line arguments
parser = argparse.ArgumentParser(description='Download files from S3 bucket')
parser.add_argument('--subject', type=str, help='subject id, including prefix, e.g sub-01133')
parser.add_argument('--model', type=str, help='model type in config task file, e.g. hcp or alt')
parser.add_argument('--config', type=str, help='path to configuration file with task / model details')
parser.add_argument('--analysisout', type=str, help='Output folder for analyses')
parser.add_argument('--workdir', type=str, help='Working directory for copy and holidng events/bold files, default /tmp/', default='/tmp/')
parser.add_argument('--logfile', type=str, help='path where to print out preprocessing details, default current dir', default='./' )
args = parser.parse_args()

# Configuration from command line args
subj_id = args.subject
studydetails_path=args.config
modtype=args.model
output_folder = args.analysisout
working_folder = args.workdir
outlog = args.logfile

# set variables and paths
user = os.getenv("USER", "unknown")
eventsdir = "/home/feczk001/mdemiden/data/hcp_events"
brain_mni_mask = "/home/feczk001/mdemiden/slurm_ABCD_s3/hcpya_preprocess/scripts/taskbold/masks/MNI152NLin2009cAsym_res-02_desc-brain_mask.nii.gz"
task_list = ['motor','gambling','language','social','WM','emotion', 'relational']
ses = "ses-3T"
logfile_name = f"{ses}_modelsran.csv"
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
        # Log the absence of runs
        log_file_path = os.path.join(outlog, logfile_name)
        log_entry = f"{date.today()},{user},{subj_id},{modtype},{task},NA,NA,NA,NA\n"
        os.system(f'echo "{log_entry.strip()}" >> {log_file_path}')
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

        # grab events and process data
        event_path = next(Path(working_folder).glob(f"{subj_id}_{ses}_task-{events_taskname}_dir-*_run-{run}_events.tsv"), None)
        if event_path is None:
            print(f"Error: Events file not found for {subj_id} {task} run-{run}")
            continue
    
        event_df = pd.read_csv(event_path, sep = '\t')
        eventdf_cpy = event_df[event_df['trial_type'].isin(mod_config['trialtype_filter'])].copy()
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
        elif task == 'WM':
            events_dat = prep_wm_events(**common_params, new_trialcol_name='new_trialtype')
        elif task == 'emotion':
            events_dat = prep_emotion_events(**common_params, new_trialcol_name='new_trialtype')
        elif task == 'relational':
            events_dat = prep_relation_events(**common_params, new_trialcol_name='new_trialtype')

        # conf files
        conf_fullpath = f"{subj_id}_{ses}_task-{bold_taskname}_dir-*_run-{run}_desc-confounds_timeseries.tsv"
        conf_path = next(Path(working_folder).glob(conf_fullpath), None)

       # Locate BOLD file
        bold_path = next(Path(working_folder).glob(f"{subj_id}_{ses}_task-{bold_taskname}_dir-*_run-{run}_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz"), None)
        if bold_path is None:
            print(f"Error: BOLD file not found for {subj_id} {task} run-{run}")
            continue

        bold_volumes = get_numvolumes(nifti_path_4d=bold_path)
        if bold_volumes != n_vols:
            print(f"Warning: Mismatch in expected ({n_vols}) vs actual BOLD volumes ({bold_volumes})")



        # Create the design matrix
        if task in ['gambling', 'social', 'WM']:
            design_matrix = create_design_matrix(
                eventdf=events_dat, conf_path=conf_path, 
                conflist_filt=mod_config['nuisance_regressors'], 
                stc=bool(config['slice_time_corr']), mod_dict=mod_config, 
                volumes=bold_volumes, time_rep=float(config['boldtr']), 
                hrf_type=config['hrf_type'], driftmod=detrend, 
                highpass=highpass, trialtype_colname='new_trialtype',
                duration_nan='replace'
            )
        else:
            design_matrix = create_design_matrix(
                eventdf=events_dat, conf_path=conf_path, 
                conflist_filt=mod_config['nuisance_regressors'], 
                stc=bool(config['slice_time_corr']), mod_dict=mod_config, 
                volumes=bold_volumes, time_rep=float(config['boldtr']), 
                hrf_type=config['hrf_type'], driftmod=detrend, 
                highpass=highpass, duration_nan='replace'
            )
        # VIFs ESTIMATE WITH ALL TASK REGRESSORS
        filtered_columns = design_matrix.columns[~design_matrix.columns.str.contains(mod_config['nuisance_regressors'], regex=True)]
        reg_dict = {item: item for item in filtered_columns if item != "constant"}
        con_vifs = est_contrast_vifs(desmat=design_matrix, contrasts=mod_config['contrasts'])
        reg_vifs = est_contrast_vifs(desmat=design_matrix, contrasts=reg_dict)
        # create / save figures
        fig = plot_design_vifs(designmat=design_matrix, regressor_vifs=reg_vifs, contrast_vifs=con_vifs, task_name=task)
        save_desvifs = f"{firstlvl}/figures/{task}_design_vifs.png"
        fig.savefig(save_desvifs, dpi=300, bbox_inches='tight')
        plt.close()

        fig, _, _ = visualize_contrastweights(design_matrix=design_matrix, config_contrasts=mod_config['contrasts'], var_exclude=mod_config['nuisance_regressors'])
        save_con = f"{firstlvl}/figures/{task}_contrasts.png"
        fig.savefig(save_con, dpi=300, bbox_inches='tight')
        plt.close()

        # check brain mask errors w/ dice coeff 
        mask_fullpath = next(Path(working_folder).glob(f"{subj_id}_{ses}_task-{bold_taskname}_dir-*_run-{run}_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz"))
        dice_coeff = image_similarity(imgfile1=brain_mni_mask, imgfile2=mask_fullpath, similarity_type='dice')

        if dice_coeff > .70:
            # Running firstlvl function
            firstglm_res = run_firstlvl_computecons(
                subjid=subj_id, 
                boldpath=bold_path, 
                designmatrix=design_matrix, 
                sesid=ses, 
                taskname=task, 
                runnum=run, 
                boldtr=float(config['boldtr']), 
                brain_mask=brain_mni_mask, 
                contrastlist=mod_config["contrasts"], 
                firstlvl_out=firstlvl,
                fwhm=fwhm, 
                ar_mod=ar_noisemod, 
                detrend=detrend, 
                highpass=highpass
            )            
            firstlvl_ran = 1
            print("First Level Model successfully ran")
        else:
            firstlvl_ran = 0
            print(f"Error in brain coverage: {subj_id} for {bold_taskname} run-{run} Brain Mask ~ MNI Overlap: {dice_coeff}.")

    if len(runs) > 1:
        compute_fixedeff(subjid=subj_id, task=task, sess_lab=ses, condict=mod_config["contrasts"], 
                 inpfold=firstlvl, outfold=fixedeff,prec_weight=False)
        fixedeff_ran = 1
        print("Fixed Effects successfully ran")
    else:
        fixedeff_ran = 0
        print(f"{subj_id} for {task} contains <2 runs (e.g runs: {len(runs)})")


    # log and append
    log_file_path = os.path.join(outlog, logfile_name)
    log_entry = f"{date.today()},{user},{subj_id},{modtype},{task},{run},{dice_coeff},{firstlvl_ran},{fixedeff_ran}\n"
    os.system(f'echo "{log_entry.strip()}" >> {log_file_path}')