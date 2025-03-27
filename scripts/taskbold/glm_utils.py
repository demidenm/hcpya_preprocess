import subprocess
import nbformat 
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from IPython.display import display, Markdown
from statsmodels.stats.outliers_influence import variance_inflation_factor
from nilearn.glm.first_level import FirstLevelModel
from nilearn.glm.second_level import SecondLevelModel
from nilearn.plotting import plot_design_matrix
from nilearn.glm.first_level import make_first_level_design_matrix
from nilearn.glm import expression_to_contrast_vector, compute_fixed_effects
from nilearn.image import load_img, new_img_like
from matplotlib.gridspec import GridSpec
from bids.layout import parse_file_entities
from nilearn.plotting.matrix_plotting import pad_contrast_matrix


# below est_contrast_vifs code is courtsey of Jeanette Mumford's repo: https://github.com/jmumford/vif_contrasts
def est_contrast_vifs(desmat, contrasts):
    """
    IMPORTANT: This is only valid to use on design matrices where each regressor represents a condition vs baseline
     or if a parametrically modulated regressor is used the modulator must have more than 2 levels.  If it is a 2 level modulation,
     split the modulation into two regressors instead.

    Calculates VIF for contrasts based on the ratio of the contrast variance estimate using the
    true design to the variance estimate where between condition correaltions are set to 0
    desmat : pandas DataFrame, design matrix
    contrasts : dictionary of contrasts, key=contrast name,  using the desmat column names to express the contrasts
    returns: pandas DataFrame with VIFs for each contrast
    """
    desmat_copy = desmat.copy()
    # find location of constant regressor and remove those columns (not needed here)
    desmat_copy = desmat_copy.loc[
        :, (desmat_copy.nunique() > 1) | (desmat_copy.isnull().any())
    ]
    # Scaling stabilizes the matrix inversion
    nsamp = desmat_copy.shape[0]
    desmat_copy = (desmat_copy - desmat_copy.mean()) / (
        (nsamp - 1) ** 0.5 * desmat_copy.std()
    )
    vifs_contrasts = {}
    for contrast_name, contrast_string in contrasts.items():
        try:
            contrast_cvec = expression_to_contrast_vector(
                contrast_string, desmat_copy.columns
            )
            true_var_contrast = (
                contrast_cvec
                @ np.linalg.inv(desmat_copy.transpose() @ desmat_copy)
                @ contrast_cvec.transpose()
            )
            # The folllowing is the "best case" scenario because the between condition regressor correlations are set to 0
            best_var_contrast = (
                contrast_cvec
                @ np.linalg.inv(
                    np.multiply(
                        desmat_copy.transpose() @ desmat_copy,
                        np.identity(desmat_copy.shape[1]),
                    )
                )
                @ contrast_cvec.transpose()
            )
            vifs_contrasts[contrast_name] = true_var_contrast / best_var_contrast
        except Exception as e:
            print(f"Error computing VIF for regressor '{contrast_name}': {e}")

    return vifs_contrasts



def plot_design_vifs(designmat, regressor_vifs, contrast_vifs, task_name):
    """
    combined figure with design matrix on the left and VIF plots on the right.
    
    Parameters:
        designmat: The design matrix
        regressor_vifs : DataFrame with VIF values for regressors
        contrast_vifs : dict or Series VIF values for contrasts
        task_name : Name of the task for plot titles
    Returns:
        multipanel fig
    """
    
    # create fix
    fig = plt.figure(figsize=(15, 10))
    grids = GridSpec(2, 2, width_ratios=[1.5, 1], height_ratios=[1, 1])
    
    #  design matrix (plot on left)
    ax1 = fig.add_subplot(grids[:, 0])  # Spans both rows in first column
    design_ax = plot_design_matrix(designmat, ax=ax1)
    ax1.set_title(f'Design Matrix: {task_name}', fontsize=14)
    
    # regressor VIFs (top right)
    ax2 = fig.add_subplot(grids[0, 1])
    contrast_series = pd.Series(regressor_vifs)
    contrast_series.plot(kind='bar', color=['#3c73a8'], ax=ax2)
    ax2.set_ylim(0, 20)
    ax2.set_xlabel('Regressors')
    ax2.set_ylabel('VIF')
    ax2.axhline(y=5, color='r', linestyle='--')
    ax2.set_title(f'Variance Inflation Factor: Regressors in {task_name}', fontsize=12)
    ax2.tick_params(axis='x', rotation=90, labelsize=11)
    
    # contrast VIFs (bottom right)
    ax3 = fig.add_subplot(grids[1, 1])
    contrast_series = pd.Series(contrast_vifs)
    contrast_series.plot(kind='bar', color=['#3c73a8'], ax=ax3)
    ax3.set_ylim(0, 20)
    ax3.set_xlabel('Contrasts')
    ax3.set_ylabel('VIF')
    ax3.axhline(y=5, color='r', linestyle='--')
    ax3.set_title(f'Variance Inflation Factor across Contrasts', fontsize=12)
    ax3.tick_params(axis='x', rotation=90, labelsize=11)
    
    plt.tight_layout()
    return fig


def generate_tablecontents(notebook_name, auto_number=True):
    """Generate a Table of Contents from markdown headers in the current Jupyter Notebook.
    *******
    ** Function recommended by claude for table of contents formatting. Iteratively fixed in code
    *******

    Parameters:
        notebook_name (str): Name of the notebook file to process
        auto_number (bool): Whether to automatically number headers (default: True)
    Returns:
        tables of contents for headers in notebook
    """
    toc = ["# Table of Contents\n"]
    
    # Counters for header levels
    counters = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    current_level = 0
    
    try:
        # Get the notebook file path
        notebook_path = os.getcwd()
        notebook_file = os.path.join(notebook_path, notebook_name)
        
        if not os.path.exists(notebook_file):
            print(f"Notebook file '{notebook_name}' not found in '{notebook_path}'.")
            return
        
        # Load the notebook content
        with open(notebook_file, "r", encoding="utf-8") as f:
            notebook = nbformat.read(f, as_version=4)

        # Collect headers
        headers = []
        for cell in notebook.cells:
            if cell.cell_type == "markdown":  # Only process markdown cells
                lines = cell.source.split("\n")
                for line in lines:
                    # Match headers with optional existing numbering
                    match = re.match(r"^(#+)\s+((?:[\d.]+\s+)?)(.*)", line)
                    if match:
                        level = len(match.group(1))  # Number of `#` determines header level
                        existing_number = match.group(2).strip()  # Capture section number if present
                        header_text = match.group(3).strip()  # Extract actual text
                        headers.append((level, existing_number, header_text))
        
        # Process headers and create TOC
        for level, existing_number, header_text in headers:
            # Strip any existing numbers from the header text for the anchor
            original_header = header_text
            
            # Auto-numbering logic for display (but not for anchors)
            display_number = ""
            if auto_number:
                # Reset lower-level counters when moving to higher level
                if level < current_level:
                    for i in range(level + 1, 7):
                        counters[i] = 0
                
                # Increment the counter for current level
                if level == 1:
                    counters[1] += 1
                    display_number = f"{counters[1]}. "
                elif level > 1:
                    # Only increment if it's a new section at this level
                    if level > current_level:
                        counters[level] += 1
                    else:
                        counters[level] += 1
                    
                    # Build the section number (e.g., "1.2.3.")
                    display_number = ""
                    for i in range(1, level + 1):
                        display_number += f"{counters[i]}."
                    display_number += " "
                
                current_level = level
            elif existing_number:
                display_number = f"{existing_number} "
            
            # Create the display text with numbering
            display_text = f"{display_number}{original_header}"
            
            # Create the anchor exactly as Jupyter would
            # Jupyter preserves the case but replaces spaces with hyphens
            anchor = original_header.replace(" ", "-")
            
            # Add entry to TOC with proper indentation
            toc.append(f"{'  ' * (level - 1)}- [{display_text}](#{anchor})")

        # Display table of contents in markdown
        display(Markdown("\n".join(toc)))
        
    except Exception as e:
        print(f"Error generating table of contents: {str(e)}")


def get_numvolumes(nifti_path_4d):
    """
    Alternative method to get number of volumes using Nilearn.
    
    Parameters:
    nifti_path(str) : Path to the fMRI NIfTI (.nii.gz) file
    
    Returns:
    Number of volumes in the fMRI data using nilearn image + shape
    """
    try:
        # Load 4D image
        img = load_img(nifti_path_4d)
        
        # Get number of volumes
        return img.shape[3] if len(img.shape) == 4 else None
    
    except Exception as e:
        print(f"Nilearn error reading file {nifti_path_4d}: {e}")
        return None


def run_firstlvl_computecons(subjid, boldpath, designmatrix, sesid, boldtr, taskname, runnum, firstlvl_out,
                             brain_mask, contrastlist, fwhm, ar_mod, detrend, highpass):
    """
    Fits a first-level fMRI [Nilearn] model and computes contrasts.
    
    Parameters:
        subjid (str): Subject identifier.
        boldpath (str): Path to the BOLD fMRI data.
        designmatrix (DataFrame): Design matrix for GLM.
        sesid (str): Session label.
        contrastlist (list): List of contrasts to iterate over.
        firstlvl_out (str): Output folder for first-level results.
        taskname (str): Task name.
        runnum (str): Run identifier.
        brain_mask (str): Path to brain mask in MNI space.
        boldtr (float): TR for BOLD data.
        fwhm (float): Smoothing kernel full-width at half maximum.
        ar_mod (str): Noise model specification.
        detrend (str): Drift model specification.
        highpass (float): High-pass filter cutoff.
    
    Returns:
        FirstLevelModel: GLM results from FirstLevelModel.fit().
    """
    fmri_glm = FirstLevelModel(
        subject_label=subjid,
        mask_img=brain_mask,
        t_r=boldtr,
        smoothing_fwhm=fwhm,
        standardize=False,
        noise_model=ar_mod,
        drift_model=detrend,
        high_pass=highpass
    )
    
    run_fmri_glm = fmri_glm.fit(boldpath, design_matrices=designmatrix)

    compute_save_contrasts(
        glm_res=run_fmri_glm, 
        sess_lab=sesid, 
        condict=contrastlist, 
        outfold=firstlvl_out, 
        subjid=subjid, 
        task=taskname, 
        run=runnum
    )
    
    return run_fmri_glm


def compute_save_contrasts(glm_res, sess_lab, condict, outfold, subjid, task, run):
    """
    Using nilearn's compute_constrast on FirstLevelModel.fit object to computed contrasts based on keys / weights in dictionary
    Weights should be associated column names in design matrix
    
    Parameters:
        glm_res: The first lvl object with fit results
        sess_lab: session label, including prefix, e.g "ses-01" or "ses-3T"
        condict: Dictionary of contrast names and their weights
        outfold: Output directory path
        subjid: Subject ID (e.g., sub-120444)
        task: Task name 
        run: Run number (e.g. 1, 2, 01, 02)
        
    Returns:
        Nothing, saves variance and beta NIFTIs
    """
    
    for con_name, con in condict.items():
        output_dir = Path(outfold)
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"    Working on contrast {con_name} with weight {con}")
        try:
            # Construct file paths
            beta_name = Path(outfold) / f"{subjid}_{sess_lab}_task-{task}_run-{run}_contrast-{con_name}_stat-beta.nii.gz"
            var_name = Path(outfold) / f"{subjid}_{sess_lab}_task-{task}_run-{run}_contrast-{con_name}_stat-var.nii.gz"
            z_name = Path(outfold) / f"{subjid}_{sess_lab}_task-{task}_run-{run}_contrast-{con_name}_stat-zscore.nii.gz"

            # Compute and save beta (effect size)
            beta_est = glm_res.compute_contrast(con, output_type="effect_size")
            beta_est.to_filename(beta_name)
            
            # Compute and save variance
            var_est = glm_res.compute_contrast(con, output_type="effect_variance")
            var_est.to_filename(var_name)

            # Compute and save z-score
            z_est = glm_res.compute_contrast(con, output_type="z_score")
            z_est.to_filename(z_name)
            
            print(f"        Successfully saved contrast {con_name}")
            
        except Exception as e:
            print(f"        First Level Error {e} for subject {subjid} and contrast {con_name}")
            continue


def compute_fixedeff(subjid: str, sess_lab: str, task: str, condict: dict, inpfold: str, outfold: str, prec_weight: bool = False, brainmask=None):
    """
    Using nilearn's compute_fixed_effects on FirstLevelModel output effect / variance files to compute fixed effect images based
    on list of contrasts.

    Parameters:
        subjid (str): Subject ID (e.g., sub-120444)
        sess_lab (str): Session label, including prefix, e.g., "ses-01" or "ses-3T"
        task (str): Task name
        condict (dict): Dictionary of contrast names and their weights
        inpfold (str): Folder path for location of first-level output beta/variance files
        outfold (str): Output directory to save fixed effect images
        prec_weight (bool): If to use precision-weighted averaging, default=False
        brainmask (str or None): Path to brain mask to use, default=None

    Returns:
        None: Saves stat, variance, and z-stat NIFTIs.
    """

    output_dir = Path(outfold)
    output_dir.mkdir(parents=True, exist_ok=True)

    for con_name in condict.keys():
        print(f"    Working on contrast: {con_name}")

        try:
            # Get matching files
            betafiles = sorted(Path(inpfold).glob(f"{subjid}_{sess_lab}_task-{task}_run-*_contrast-{con_name}_stat-beta.nii.gz"))
            varfiles = sorted(Path(inpfold).glob(f"{subjid}_{sess_lab}_task-{task}_run-*_contrast-{con_name}_stat-var.nii.gz"))

            # Ensure matched files exist
            if len(betafiles) != len(varfiles):  
                raise ValueError(f"Mismatch: {len(betafiles)} beta files vs. {len(varfiles)} variance files.")

            if len(betafiles) < 2:
                raise ValueError("Found fewer than two files, nothing to average over.")

            # Compute fixed effects
            fixmap, fixvar, _, fixzscore = compute_fixed_effects(
                contrast_imgs=betafiles, variance_imgs=varfiles, 
                mask=brainmask, precision_weighted=prec_weight, dofs=None, return_z_score=True
            )

            # Save outputs
            for stat, suffix in zip([fixmap, fixvar, fixzscore], ["fixeff", "fixvar", "fixzscore"]):
                filename = output_dir / f"{subjid}_{sess_lab}_task-{task}_contrast-{con_name}_stat-{suffix}.nii.gz"
                stat.to_filename(filename)


            print(f"        Successfully saved files for contrast: {con_name}")

        except Exception as e:
            print(f"        Fixed Effect Error: {e} for subject {subjid}, contrast {con_name}")
            continue


def create_design_matrix(eventdf, stc: bool, conf_path: str, conflist_filt: list, 
                         mod_dict: dict, time_rep: float, volumes: int, hrf_type: str = 'spm',
                         driftmod: str = None, highpass: float = None, trialtype_colname: str = None, duration_nan='replace'):
    """
    Generates a first-level design matrix for fMRI analysis.

    Parameters:
        eventdf (pd.DataFrame): Dataframe containing event information.
        stc (bool): Whether slice time correction was performed during fMRIPrep.
        conf_path (str): Path to the confounds file (tab-separated).
        conflist_filt (list): List of column names to filter from confounds.
        mod_dict (dict): Dictionary containing model parameters (onsets, durations, trial type column names).
        time_rep (float): Time repetition for data
        volumes (int): Number of volumes in the fMRI scan.
        hrf_type (str): HRF model for design matrix (e.g., "glover", "spm").
        driftmod (str, optional): Drift model parameter (e.g., polynomial, cosine). Default is None (for fMRIPrep).
        highpass (float, optional): High-pass filter frequency in Hz. Required if `driftmod` is "cosine".
        trialtype_colname (str): If different from trial_type, specify
        duration_nan (str): whether to 'drop' or 'replace' with 0 duration 'NaN' columns, default replace

    Returns:
        pd.DataFrame: The generated design matrix.
    """

    # Ensure required eventdf columns exist
    if trialtype_colname:
        trialtype_lab = trialtype_colname
    else:
        trialtype_lab = mod_dict['trialtype_colname']
    
    required_columns = {trialtype_lab, mod_dict['onset_colname'], mod_dict['duration_colname']}
    if not required_columns.issubset(eventdf.columns):
        missing_cols = required_columns - set(eventdf.columns)
        raise ValueError(f"Missing required columns in eventdf: {missing_cols}")

    # Load confounds data
    conf_df = pd.read_csv(conf_path, sep='\t')

    # Create design events DataFrame
    design_events = pd.DataFrame({
        'trial_type': eventdf[trialtype_lab],
        'onset': eventdf[mod_dict['onset_colname']], 
        'duration': eventdf[mod_dict['duration_colname']]
    })

    if design_events["duration"].isna().any():
        print(f"Warning: Found {design_events.isna().sum()} NaN values in duration column")
        if duration_nan == "replace":
            design_events["duration"].fillna(0, inplace=True)
        elif duration_nan == "drop":
            design_events = design_events.dropna(subset=['onset'])
        else:
            raise ValueError(duration_nan, "is not of drop or replace")

    # Set frame times
    frame_times = np.arange(volumes) * time_rep

    # Apply slice time correction if needed
    if stc:
        frame_times += time_rep / 2  # Shift onsets by TR/2

    # grab confounds
    try:
        confounds_filtered = conf_df.filter(regex=f"^({conflist_filt})").fillna(0)  # Replace NaNs with 0
    except Exception as e:
        raise ValueError(f" Error processing confounds: {e}")

    # create design matrix
    try:
        design_matrix = make_first_level_design_matrix(
            frame_times=frame_times, events=design_events,
            hrf_model=hrf_type, drift_model=driftmod, high_pass=highpass,
            add_regs=confounds_filtered
        )
        print(f"    For variables in confounds: {conflist_filt}, NaNs were replaced with 0")
    except Exception as e:
        raise RuntimeError(f"   Error creating design matrix: {e}")

    return design_matrix


def visualize_contrastweights(design_matrix, config_contrasts, var_exclude):
    """
    Heatmap of contrast weights
    
    Parameters:
    design_matrix (pd.DataFrame):  The design matrix containing regressors for the model
    config_contrasts (dict): Configuration dictionary with 'contrasts' items and keys
    var_exclude (list): List of nuisance regressors to exclude
        
    Returns:
    --------
    fig: The figure object containing the heatmap
    contrast_weights: Dictionary mapping contrast IDs to their weight vectors
    weights_df: DataFrame containing all contrast weights
    """
    all_weights = []
    contrast_names = []
    contrast_weights = {}
    
    # exclude nuisance regressors from design colnames
    subset_cols_design = design_matrix.columns[~design_matrix.columns.str.contains(var_exclude, regex=True)]
    column_names = subset_cols_design.tolist()
    
    # iterate over contrats and save to lists
    for contrast_id, contrast_def in config_contrasts.items():
        weights = pad_contrast_matrix(contrast_def, design_matrix[subset_cols_design])
        contrast_weights[contrast_id] = weights
        all_weights.append(weights)
        contrast_names.append(contrast_id)
        
    # convert to df
    weights_df = pd.DataFrame(
        all_weights, 
        index=contrast_names,
        columns=column_names
    )

    min_width = 12
    min_height = 6
    computed_height = len(contrast_names) * 0.8
    fig_height = max(computed_height, min_height)

    fig, ax = plt.subplots(figsize=(min_width, fig_height))
    sns.heatmap(weights_df, cmap="RdBu_r", center=0, annot=True, fmt=".2f",      
        linewidths=.5, cbar_kws={"label": "Contrast Weight"}, ax=ax, vmin=-1, vmax=1  

    )
    
    # customize details
    ax.set_title("Contrast Weights", fontsize=12)
    ax.set_xlabel("Regressor Names", fontsize=10)
    ax.set_ylabel("Contrast Name", fontsize=10)
    
    plt.xticks(rotation=90, ha="right")
    plt.yticks(rotation=45, ha="right")
    plt.tight_layout()
    
    return fig, contrast_weights, weights_df


def nifti_tstat_to_cohensd(tstat_path:str, sample_n: int):
    """
    Function converts NIfTI t-statistic image to Cohen's d.

    Parameters:
    tstat_path (str): Path to NIfTI image containing t-statistic nifti volume.
    sample_n (int): Sample size make up t-stat for calculating Cohen's d
    
    Returns:
    NIfTI image containing Cohen's d.
    """
    
    t_img = nib.load(tstat_path)
    # Get data array from the t-statistics image
    t_data = t_img.get_fdata()
    # Calculate Cohen's d using the t_stat / sqrt(n) formula
    d_data = t_data / np.sqrt(sample_n)
    # Create a NIfTI image containing Cohen's d, with the same properties as the input image
    cohensd_img = new_img_like(t_img, d_data)

    return cohensd_img


def group_onesample(fixedeffect_paths: list, session: str, task_type: str,
                    contrast_type: str, group_outdir: str,
                    mask: str = None, save_zscore: bool = True, save_cohensd: bool = True):
    """
    Computes a group (second-level) model by fitting an intercept to the length of maps.
    Saves computed statistics to disk.
    """    
    group_outdir = Path(group_outdir)  
    group_outdir.mkdir(parents=True, exist_ok=True)
    print("Directory ensured:", group_outdir)
    
    fixedeffect_paths = [str(path) for path in fixedeffect_paths]
    n_maps = len(fixedeffect_paths)
    design_matrix = pd.DataFrame([1] * n_maps, columns=['int'])


    # Fit second-level model
    sec_lvl_model = SecondLevelModel(mask_img=mask, smoothing_fwhm=None, minimize_memory=False)
    sec_lvl_model = sec_lvl_model.fit(second_level_input=fixedeffect_paths, design_matrix=design_matrix)

    tstat_map = sec_lvl_model.compute_contrast(
        second_level_contrast='int',
        second_level_stat_type='t',
        output_type='stat'
    )

    tstat_out = group_outdir / f"subs-{n_maps}_{session}_task-{task_type}_contrast-{contrast_type}_stat-tstat.nii.gz"
    tstat_map.to_filename(tstat_out)

    if save_cohensd:
        cohensd_out = tstat_out.replace('tstat', 'cohensd')
        cohensd_map = nifti_tstat_to_cohensd(tstat_map=tstat_out,sample_n=n_maps)
        cohensd_map.to_filename(cohensd_out)

    if save_zscore:
        zstat_map = sec_lvl_model.compute_contrast(
        second_level_contrast='int',
        second_level_stat_type='t',
        output_type='z_score'
        )
        zstat_out = group_outdir / f"subs-{n_maps}_{session}_task-{task_type}_contrast-{contrast_type}_stat-zscore.nii.gz"
        zstat_map.to_filename(zstat_out)


def get_files(bash_command):
    command_out = subprocess.run(bash_command, shell=True, capture_output=True, text=True)
    files = [line.split()[-1] for line in command_out.stdout.strip().split("\n") if line]
    
    return files

    
def sync_matching_runs(subject_id, sesid, taskname, events_path, sync_destination):
    """
    Syncs the matching fMRIPrep bold, confounds, mask, and event files for a given task and subject.

    Parameters:
        subject_id (int): Subject ID
        sesid (str): Session full string (e.g., ses-3T)
        taskname (str): Task name (e.g., motor)
        events_path (str): Path to local event files
        sync_destination (str): Destination to copy matching files to for analyses

    Returns:
        Runs found (list) or 'None' (str)
    """

    # Get fMRIPrep bold and mask files from S3

    fmriprep_boldlist = f"s3cmd ls --recursive s3://hcp-youth/derivatives/fmriprep_v24_0_1/{sesid}/{subject_id}/{sesid}/func/ | grep 'task-{taskname}_dir.*_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz'"
    bold_files = get_files(fmriprep_boldlist)
    fmriprep_masklist = f"s3cmd ls --recursive s3://hcp-youth/derivatives/fmriprep_v24_0_1/{sesid}/{subject_id}/{sesid}/func/ | grep 'task-{taskname}_dir.*_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz'"
    mask_files = get_files(fmriprep_masklist)
    confounds_list = f"s3cmd ls --recursive s3://hcp-youth/derivatives/fmriprep_v24_0_1/{sesid}/{subject_id}/{sesid}/func/ | grep 'task-{taskname}_dir.*_desc-confounds_timeseries.tsv'"
    confounds_files = get_files(confounds_list)

    # Get events list
    events_list = f"ls {events_path}/{subject_id}/{sesid}/func/ | grep 'task-{taskname}.*_events.tsv'"
    event_files = get_files(events_list)

    # Match task and run consistency
    matched_runs = {}
    for bold_file in bold_files:
        bold_metadata = parse_file_entities(bold_file)
        bold_task = bold_metadata.get("task")
        bold_run = bold_metadata.get("run")

        # Find the corresponding confounds and mask files
        confound_file = next((cf for cf in confounds_files if f"run-{bold_run}" in cf), None)
        mask_file = next((mf for mf in mask_files if f"run-{bold_run}" in mf), None)

        for event_file in event_files:
            event_metadata = parse_file_entities(event_file)
            event_task = event_metadata.get("task")
            event_run = event_metadata.get("run")

            if bold_task == event_task and bold_run == event_run and confound_file and mask_file:
                matched_runs[bold_run] = (bold_file, mask_file, confound_file, event_file)

    # Sync only matching runs
    if not matched_runs:
        return [], None, None

    sync_commands = []
    for run, (bold_file, mask_file, confound_file, event_file) in matched_runs.items():
        bold_sync_cmd = f"s3cmd get {bold_file} {sync_destination}/ --continue"
        mask_sync_cmd = f"s3cmd get {mask_file} {sync_destination}/ --continue"
        confound_sync_cmd = f"s3cmd get {confound_file} {sync_destination}/ --continue"
        event_sync_cmd = f"cp {events_path}/{subject_id}/{sesid}/func/{event_file} {sync_destination}/"

        subprocess.run(bold_sync_cmd, shell=True)
        subprocess.run(mask_sync_cmd, shell=True)
        subprocess.run(confound_sync_cmd, shell=True)
        subprocess.run(event_sync_cmd, shell=True)

        sync_commands.append((bold_sync_cmd, mask_sync_cmd, confound_sync_cmd, event_sync_cmd))

    return list(matched_runs.keys()), bold_task, event_task


def gen_vifdf(designmat, modconfig):
    """
    Create a Pandas DataFrame with VIF values for contrasts and regressors.

    Parameters
    designmat: The design matrix used in the analysis.
    modconfig (dict): A dictionary containing model configuration, including:
        - 'nuisance_regressors': A regex pattern to filter out nuisance regressors.
           - 'contrasts': A dictionary of contrast definitions.

    Returns
    Returns contrasts & regressors vif dict & DataFrame of combined VIFs w/ columns ['type', 'name', 'value'].
    """
    # Filter columns by removing nuisance regressors & create dictionary that excludes constant
    filtered_columns = designmat.columns[~designmat.columns.str.contains(modconfig['nuisance_regressors'], regex=True)]
    regressor_dict = {item: item for item in filtered_columns if item != "constant"}

    # Function to filter out non-existent regressors
    def filter_existing_regressors(contrast_dict):
        return {
            k: v for k, v in contrast_dict.items() 
            if all(col in designmat.columns for col in v.split('-') if col.strip())
        }

    # Filter contrasts to include only those with existing regressors
    filtered_contrasts = filter_existing_regressors(modconfig['contrasts'])
    
    # est VIFs for contrasts and regressors
    con_vifs = est_contrast_vifs(desmat=designmat, contrasts=modconfig['contrasts'])
    reg_vifs = est_contrast_vifs(desmat=designmat, contrasts=regressor_dict)

    # convert to do
    df_con = pd.DataFrame(list(con_vifs.items()), columns=["name", "value"])
    df_con["type"] = "contrast"
    df_reg = pd.DataFrame(list(reg_vifs.items()), columns=["name", "value"])
    df_reg["type"] = "regressor"

    # combine & rename cols
    df = pd.concat([df_con, df_reg], ignore_index=True)
    df = df[["type", "name", "value"]]

    return con_vifs, reg_vifs, df