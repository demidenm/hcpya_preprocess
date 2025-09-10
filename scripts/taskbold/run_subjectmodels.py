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
get_files, sync_matching_runs, gen_vifdf, extract_timeseries_atlas, binarize_nifti, calc_boldvar)
from prep_eventsdata import (comb_names, prep_gamble_events, prep_motor_events, 
prep_social_events, prep_language_events, prep_relation_events, prep_emotion_events, prep_wm_events)
from pyrelimri.similarity import image_similarity
from nilearn.image import math_img
plt.switch_backend('Agg') # turn off back end display to create plots


# Parse command line arguments
parser = argparse.ArgumentParser(description='Download files from S3 bucket')
parser.add_argument('--subject', type=str, help='subject id, including prefix, e.g sub-01133')
parser.add_argument('--model', type=str, help='model type in config task file, e.g. hcp or alt')
parser.add_argument('--config', type=str, help='path to configuration file with task / model details')
parser.add_argument('--analysisout', type=str, help='Output folder for analyses')
parser.add_argument('--workdir', type=str, help='Working directory for copy and holidng events/bold files, default /tmp/', default='/tmp/')
parser.add_argument('--logfile', type=str, help='path where to print out analysis details, default current dir', default='./' )
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
vifs_sub = f"{output_folder}/vifs/{subj_id}"
os.makedirs(firstlvl, exist_ok=True)
os.makedirs(fixedeff, exist_ok=True)
os.makedirs(vifs_sub, exist_ok=True)
os.makedirs(f"{firstlvl}/figures", exist_ok=True)

# task, model specs
with open(studydetails_path, 'r') as file:
    study_details = json.load(file)

# saving complete vif df
all_vif_dfs = []
match_tasks = 0

for task in task_list:    
    print(f"Starting task: {task}")
    runs, bold_taskname, events_taskname = sync_matching_runs(subject_id=subj_id, sesid=ses, taskname=task, 
    events_path=eventsdir, sync_destination=working_folder)

    if not runs:
        print(f"No matching runs found for subject {subj_id} and task {task}")
        # Log the absence of runs
        log_file_path = os.path.join(outlog, logfile_name)
        log_entry = f"{date.today()},{user},{subj_id},{modtype},{task},{len(runs)},NA,NA,NA,NA\n"
        os.system(f'echo "{log_entry.strip()}" >> {log_file_path}')
        continue
    
    # for each matching task
    match_tasks += 1

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
        conf_path = next(Path(working_folder).glob(f"{subj_id}_{ses}_task-{bold_taskname}_dir-*_run-{run}_desc-confounds_timeseries.tsv"), None)

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

        # VIFs estimate with ALL task regressors
        try:
            contrast_vifs, regress_vifs, vif_df = gen_vifdf(designmat=design_matrix, modconfig=mod_config)
            vif_df['task'] = task
            vif_df['run'] = run
            
            all_vif_dfs.append(vif_df) 

            # create / save figures / design
            fig = plot_design_vifs(designmat=design_matrix, regressor_vifs=regress_vifs, contrast_vifs=contrast_vifs, task_name=task)
            save_desvifs = f"{firstlvl}/figures/{task}_design_vifs.png"
            fig.savefig(save_desvifs, dpi=300, bbox_inches='tight')
            plt.close()
            design_matrix.to_csv(f"{firstlvl}/{subj_id}_{ses}_task-{task}_run-{run}_designmatrix.tsv", sep='\t', index=False)
            
        except Exception as e:
            raise RuntimeError(f"   Error estimating VIFs: {e}")
            continue

        # check brain mask errors w/ dice coeff 
        mask_fullpath = next(Path(working_folder).glob(f"{subj_id}_{ses}_task-{bold_taskname}_dir-*_run-{run}_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz"))
        dice_coeff = image_similarity(imgfile1=brain_mni_mask, imgfile2=mask_fullpath, similarity_type='dice')

        first_coverage_prob = 0
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
            print(f"{subj_id}: First Level successfully ran for {task} run-{run}")

            # run and save timeseries matrix
            anat_gmmask = next(Path(working_folder).glob(f"*_space-MNI152NLin2009cAsym_res-2_label-GM_probseg.nii.gz"), None)            
            if anat_gmmask:
                # compute mask based on non-zero from variance and anat GM prob thresholded/binned maps
                bold_var = calc_boldvar(boldpath=bold_path)
                var_binned = binarize_nifti(nifti_path=bold_var, img_thresh=0)
                gm_binned = binarize_nifti(nifti_path=anat_gmmask, img_thresh=0.01)
                vargm_mask = math_img('img1 * img2', img1=var_binned, img2=gm_binned)

                for atlas_type in ['schaefer', 'difumo']:
                    print(f"{subj_id}: Exacting residuals timeseries for {atlas_type} atlas for {task} run-{run}")

                    if atlas_type == 'schaefer':
                        roi_dim = 1000
                    elif atlas_type == 'difumo':
                        roi_dim = 1024
                    try:

                        timeseries_dat, _ = extract_timeseries_atlas(
                            resid_nifti=firstglm_res.residuals[0], 
                            atlas_name=atlas_type, 
                            n_dimensions=roi_dim, 
                            mask_img=vargm_mask
                        )
                        timeseries_pd = pd.DataFrame(timeseries_dat)
                        timeseries_pd.to_csv(
                            Path(firstlvl) / f"{subj_id}_{ses}_task-{task}_run-{run}_atlas-{atlas_type}_rois-{roi_dim}_timeseries.tsv",
                            sep='\t' 
                        )
                        timeseries_extracted = 1
                    except Exception as e:
                        print(f"Error running {atlas_type}: {e}")
                        timeseries_extracted = 0

        else:
            first_coverage_prob += 1
            timeseries_extracted = 0
            firstlvl_ran = 0
            print(f"Error in brain coverage: {subj_id} for {bold_taskname} run-{run} Brain Mask ~ MNI Overlap: {dice_coeff}.")

    if len(runs) > 1 and first_coverage_prob == 0:
        compute_fixedeff(subjid=subj_id, task=task, sess_lab=ses, condict=mod_config["contrasts"], 
                 inpfold=firstlvl, outfold=fixedeff,prec_weight=False)
        fixedeff_ran = 1
        print(f"{subj_id}: Fixed Effect successfully ran for {task}")
    else:
        fixedeff_ran = 0
        print(f"{subj_id}: {task} contains <2 runs (e.g runs: {len(runs)}) or coverage is bad for runs ({first_coverage_prob}). Skipping Fixed Effects.")


    # log and append
    log_file_path = os.path.join(outlog, logfile_name)
    log_entry = f"{date.today()},{user},{subj_id},{modtype},{task},{len(runs)},{dice_coeff},{firstlvl_ran},{fixedeff_ran},{timeseries_extracted}\n"
    os.system(f'echo "{log_entry.strip()}" >> {log_file_path}')
    print()
    print(f"Saved to log: Date, USER, Subject, ModelType, TaskName, Runs, DiceEst, FirstLvlStatus, FixedEffStatus, Timeseries_extracted")
    print()

# save vif df if at least 1 task match runs found & isn't empty
if match_tasks > 0 and all_vif_dfs:
    final_vif_df = pd.concat(all_vif_dfs, ignore_index=True)
    vif_dif_path = f"{vifs_sub}/all-tasks_vif-estimates.tsv"
    final_vif_df.to_csv(vif_dif_path, sep="\t")