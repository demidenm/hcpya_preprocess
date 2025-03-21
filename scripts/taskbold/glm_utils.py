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
from nilearn.plotting import plot_design_matrix
from nilearn.glm.first_level import make_first_level_design_matrix
from nilearn.glm import expression_to_contrast_vector
from matplotlib.gridspec import GridSpec
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
            beta_name = Path(outfold) / f"sub-{subjid}_{sess_lab}_task-{task}_run-{run}_contrast-{con_name}_stat-beta.nii.gz"
            var_name = Path(outfold) / f"sub-{subjid}_{sess_lab}_task-{task}_run-{run}_contrast-{con_name}_stat-var.nii.gz"
            
            # Compute and save beta (effect size)
            beta_est = glm_res.compute_contrast(con, output_type="effect_size")
            beta_est.to_filename(beta_name)
            
            # Compute and save variance
            var_est = glm_res.compute_contrast(con, output_type="effect_variance")
            var_est.to_filename(var_name)
            
            print(f"        Successfully saved contrast {con_name}")
            
        except Exception as e:
            print(f"        Error processing contrast: {e} for subject {subjid}, contrast {con_name}")


def create_design_matrix(eventdf, stc: bool, conf_path: str, conflist_filt: list, 
                         mod_dict: dict, time_rep: float, volumes: int, hrf_type: str = 'spm',
                         driftmod: str = None, highpass: float = None, trialtype_colname: str = None):
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


def visualize_contrastweights(design_matrix, config_contrasts, nusiance_exclude):
    """
    Heatmap of contrast weights
    
    Parameters:
    design_matrix (pd.DataFrame):  The design matrix containing regressors for the model
    config_contrasts (dict): Configuration dictionary with 'contrasts' items and keys
    nusiance_exclude (list): List of nuisance regressors to exclude
        
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
    subset_cols_design = design_matrix.columns[~design_matrix.columns.str.contains(nusiance_exclude, regex=True)]
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
    sns.heatmap(weights_df, cmap="RdBu_r", center=0, annot=True, fmt=".1f",      
        linewidths=.5, cbar_kws={"label": "Contrast Weight"}, ax=ax, vmin=-1, vmax=1  

    )
    
    # Customize the plot
    ax.set_title("Contrast Weights", fontsize=12)
    ax.set_xlabel("Regressor Names", fontsize=10)
    ax.set_ylabel("Contrast Name", fontsize=10)
    
    plt.xticks(rotation=90, ha="right")
    plt.yticks(rotation=45, ha="right")
    plt.tight_layout()
    
    return fig, contrast_weights, weights_df