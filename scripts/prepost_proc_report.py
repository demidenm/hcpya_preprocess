import os
import pandas as pd
import subprocess
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import ptitprince as pt  

# set folders
input_dir = './'
tmp = './tmp'
output_dir = '../imgs'

grp_fold = './mriqc/group_mriqc/out_group'
qc_out = './fmriprep/post_preprocessing_checks/qc_sdc-similarity'

xcpd_out = './xcp_d/xcpd_qc-output'
roi_check = ['LH_Vis_43', 'LH_SomMot_84', 'LH_Limbic_OFC_12', 'LH_Default_PFC_40', 'RH_Limbic_OFC_1']


os.makedirs(output_dir, exist_ok=True)
os.makedirs(tmp, exist_ok=True)

plot_metrics = {
    'bold': ['fd_mean', 'fwhm_avg', 'snr', 'tsnr'],
    'T1w': ['cnr', 'fwhm_avg','snr_total'],
    'T2w': ['cnr', 'fwhm_avg','snr_total']
}

# specify preproc types & data dict
folders = ['mriqc', 'fmriprep','xcp_d']

subject_counts = {}

for preproc_type in folders:
    print(f"Working on {preproc_type}")

    subject_counts[preproc_type] = {}
    folder = os.path.join(input_dir, preproc_type)
    if os.path.exists(folder):
        # Each .tsv file in the preproc folders
        for filename in os.listdir(folder):
            if filename.endswith('.tsv'):
                session, status = filename.split('_')[:2]
                filepath = os.path.join(folder, filename)

                # Check if the file is empty
                if os.path.getsize(filepath) == 0:
                    print(f"Skipping empty file: {filename}")
                    continue

                # Create tmp for first sub column to avoid parsing errors
                tmp_file = f'{tmp}/subs_{preproc_type}_{session}{status}'
                subprocess.run(f"awk '{{ print $1 }}' {filepath} > {tmp_file}", shell=True, check=True)
                subj_count = len(pd.read_csv(tmp_file, header=None)[0].unique())

                if session not in subject_counts[preproc_type]:
                    subject_counts[preproc_type][session] = {}
                subject_counts[preproc_type][session][status] = subj_count

data = []
for preprocessing_type, sessions in subject_counts.items():
    for session, statuses in sessions.items():
        for status, count in statuses.items():
            data.append([preprocessing_type, session, status.replace('.tsv', ''), count])
df = pd.DataFrame(data, columns=['Type', 'Session', 'Status', 'Count'])

sns.set(style="whitegrid")


# Create RUN COMPLEITION PLOTS for FMRIPrep / MRIQC / XCP-D

for preprocessing_type, group_data in df.groupby('Type'):
    print(preprocessing_type, group_data)
    group_data['Status'] = pd.Categorical(group_data['Status'], categories=["completed", "failed"], ordered=True)
    
    plt.figure(figsize=(8, 6))
    ax = sns.barplot(x='Status', y='Count', hue='Session', data=group_data, palette='tab10')
    
    plt.title(preprocessing_type)
    plt.xlabel('Completion Status')
    plt.ylabel('N Completed')
    
    # add labels to top
    for p in ax.patches:
        if not pd.isna(p.get_height()):  # Skip NaN values
            ax.annotate(f'{int(p.get_height())}', 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='bottom', 
                        fontsize=10, color='black', 
                        xytext=(0, 5), 
                        textcoords='offset points')
    plt.savefig(f'{output_dir}/{preprocessing_type}_subject_counts.png')
    plt.close()


# Create Summary Plots of GROUP DERIVATIVES MRIQC

for img_key in plot_metrics.keys():
    print("Making Group Deriv MRIQC Plots")
    pull_cols = plot_metrics[img_key]
    pull_cols = ['bids_name'] + plot_metrics[img_key]
    df = pd.read_csv(f'{grp_fold}/group_{img_key}.tsv', sep='\t', usecols=pull_cols)
    
    split_items = df['bids_name'].str.split('_')

    df['session'] = split_items.str[1].str.split('ses-').str[-1]
    df['task_names'] = split_items.str[2].str.split('task-').str[-1]
    df['img_type'] = split_items.str[-1]
    df['run'] = split_items.apply(lambda x: x[4].split('run-')[-1] if len(x) > 4 and 'run-' in x[4] else '01')
        
    # accidentally ran 7T, too, but  not needed
    df = df[df['session'] != "7T"]

    columns_to_plot = plot_metrics[img_key]
    sess_list = list(df['session'].unique())
    df['run_task'] = df['task_names'] + '_' + df['run']
    
    # convert mriqc to numeric if not all ready
    for col in columns_to_plot:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # size dependenint on colums * sessions
    plt.figure(figsize=(15 * len(sess_list), len(columns_to_plot) * 5)) # w x h

    for i, col in enumerate(columns_to_plot):
        for j, sess in enumerate(sess_list):
            plt.subplot(len(columns_to_plot), len(sess_list), i * len(sess_list) + j + 1)  # Create subplot grid
            
            # Filter for session and plot each metric
            df_session = df[df['session'] == sess]
            
            # Sort data by 'run_task' for sorted x-axis labels
            df_session = df_session.sort_values(by='run_task')
            unique_hues = df_session['run'].nunique()
            ax = plt.gca()
            
            # Create the RainCloud plot
            rain = pt.RainCloud(
                x='run_task', y=col, hue='task_names', data=df_session,
                palette='Set2', bw=0.2, width_viol=0.6, orient="v",
                ax=ax
            )
            
            # Customize axis labels and titles
            if j == 0:
                ax.set_ylabel(col.upper(), fontsize=12)
            ax.set_title(f'Ses: {sess} - {col.upper()}', fontsize=14, fontweight='bold')
            
            # Sort and update x-axis labels
            ax.set_xticks(range(len(df_session['run_task'].unique())))
            sorted_labels = sorted(df_session['run_task'].unique())  # Sorted x-axis labels
            ax.set_xticklabels(sorted_labels, rotation=45)
            ax.set_xlabel("")
            
            # Modify and sort the legend
            handles, labels = ax.get_legend_handles_labels()
            sorted_indices = sorted(range(len(labels)), key=lambda k: labels[k])  # Sort legend labels
            handles = [handles[idx] for idx in sorted_indices]
            labels = [labels[idx] for idx in sorted_indices]
            

    plt.tight_layout()
    plt.savefig(f'{output_dir}/{img_key}_mriqc-plot.png')
    plt.close()

# summaries PERISTIMULUS PLOT

if os.path.exists(f'{qc_out}/3T_check-peristim.tsv'):
    print("Making Peristimulus Summary RainCloud Plots")
    peristim_df = pd.read_csv(f'{qc_out}/3T_check-peristim.tsv', sep='\t', 
                              names=['sub', 'sess', 'task', 'region', 'peak_tr', 'peak_mean', 'peak_se']).drop_duplicates(subset='sub')
    peri_sub_n = len(peristim_df)

    sns.set(style="whitegrid")
    fig, axes = plt.subplots(1, 3, figsize=(15, 10))  # 1 row, 3 columns

    # y-axis labels for each column
    y_labels = {
        'peak_tr': "Peak TR",
        'peak_mean': "Mean Signal at Peak",
        'peak_se': "SE Signal at Peak"
    }

    # columns ~ palette
    columns_of_interest = ['peak_tr', 'peak_mean', 'peak_se']
    colors = sns.color_palette("Set2", len(columns_of_interest))

    for ax, col, color in zip(axes, y_labels.keys(), colors):
        # RainCloud plot
        pt.RainCloud(
            y=col,
            data=peristim_df,
            palette=[color],  # Use a single color for this plot
            bw=0.2,
            width_viol=0.6,
            orient="v",
            ax=ax
        )
        
        ax.set_ylabel(y_labels[col]) 
        ax.set_xlabel("")

        # Expand min/max to avoid weird cut-offs
        ax.set_ylim(peristim_df[col].min() - 0.5, peristim_df[col].max() + 0.5)

    plt.subplots_adjust(wspace=0.5)  # Adjust horizontal spacing between plots
    plt.suptitle(f'Max TR (.720sec) from Peristimulus Plots across N = {peri_sub_n}', fontsize=14)
    plt.savefig(f'{output_dir}/peristim_distributions.png')
    plt.close()
else:
    print(f'\tFILE: \n{qc_out}/3T_check-peristim.tsv does not exist')


# summaries QC SIMILARITY ESTIMATES AND FMRIPREP Reports

if os.path.exists(f'{qc_out}/3T_check-html-similarity.tsv'):
    print("Making Similarity Summary Plots")
    fs_sim_df = pd.read_csv(f'{qc_out}/3T_check-html-similarity.tsv', sep = '\t', 
                          names=['sub','sess','task','run','event_files', 'sdc_type', 'sim.freesurf_anat', 'sim.anat-bold'])
    
    fs_sim_df = fs_sim_df = fs_sim_df.drop_duplicates(subset=['sub', 'task', 'run', 'sdc_type', 'event_files', 'sdc_type', 'sim.freesurf_anat', 'sim.anat-bold'])
    sub_n = len(fs_sim_df.drop_duplicates(subset='sub'))
    
    # percent non-resting runs with where events_file == exists
    task_event_exists = fs_sim_df[fs_sim_df['task'] != 'rest'].assign(
        event_files_notna=fs_sim_df['event_files'].notna()
    ).groupby('task')['event_files_notna'].mean() * 100


    plt.figure(figsize=(18, 6))

    # Percent of Tasks (not "rest") with Event Files
    plt.subplot(131)
    sns.barplot(x=task_event_exists.index, y=task_event_exists.values, palette="Set2")
    plt.title(f'Percent of Non-Rest Task Runs w/ Event Files \n across N = {sub_n} subjects')
    plt.xlabel('')
    plt.xticks(rotation=45, ha='center')
    plt.ylabel('% w/ File')

    # Distribution of `sdc_type` by Task
    plt.subplot(132)
    sns.countplot(data=fs_sim_df, x='task', hue='sdc_type', palette="Set2")
    plt.title(f'Type SDC \n per Run')
    plt.xticks(rotation=45, ha='center')
    plt.xlabel('')
    plt.ylabel('Count')

    # Distribution of `sim.freesurf_anat` and `sim.anat-bold`
    # get uniq subjects, as similarity for freesurf/anatomy mask will be redudnt for each bold run
    unique_sub_df = fs_sim_df.drop_duplicates(subset='sub')

    plt.subplot(133)
    sns.kdeplot(data=unique_sub_df['sim.freesurf_anat'], label='Dice(Freesurf, Anatmsk)', fill=True, color='b', alpha=0.6)
    sns.kdeplot(data=fs_sim_df['sim.anat-bold'], label='Dice(Anatmsk,BOLDmsk)', fill=True, color='r', alpha=0.6)
    plt.title(f'Distribution: Similarity Fressurfer ~ Native Mask \n & MNI Anat ~ BOLD masks')
    plt.xlabel('Value')
    plt.ylabel('Density')
    plt.legend(loc='upper center', ncol=2)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/qc-similarity_distributions.png')
    plt.close() 

    # Counts across runs/tasks/sdc type

    task_run_summary = fs_sim_df.groupby(['task', 'run', 'sdc_type']).size().reset_index(name='count')
    plt.figure(figsize=(10, 6))
    sns.heatmap(task_run_summary.pivot_table(index=['task', 'run'], columns='sdc_type', values='count', fill_value=0), 
                annot=True, cmap='Blues',
                fmt='d')
    plt.title(f'Task Run Counts across \n N = {sub_n} subjects')
    plt.xlabel('SDC Type')
    plt.ylabel('Task ~ Run')
    plt.savefig(f'{output_dir}/fmriprep_task-run-sdc_counts.png')
    plt.close()
else:
    print(f'\t FILE: {qc_out}/3T_check-html-similarity.tsv doesnt exist')



# plots of XCP-D QC CHECKS


if os.path.exists(f'{xcpd_out}/3T_combined-network.tsv.tsv'):
    # https://github.com/RainCloudPlots/RainCloudPlots?tab=readme-ov-file#making-rainclouds-in-python

    print("Making XCP-D Network Estimate Rainclouds")

    # load data, skip if rows are bad (e.g., unable to parse dude to inconsistent values in row)
    df = pd.read_csv(f'{xcpd_out}/3T_combined-network.tsv.tsv', sep='\t', on_bad_lines='skip', 
                     index_col=None, header=None, names=["subject","network","type","value"])
    # convert value to numeric & drop nan to avoid errors in plotting below 
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df = df.dropna(subset=['value'])

    unique_networks = df['network'].unique()
    unique_networks = unique_networks[(unique_networks != 'no_r_mat') & ~pd.isna(unique_networks)]
    
    # define cols/rows for multi-panel fig
    n_cols = 2  
    n_rows = -(-len(unique_networks) // n_cols)  

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows), constrained_layout=True)
    axes = axes.flatten()  
    palette = sns.color_palette("Set3")
    
    for i, network in enumerate(unique_networks):
        ax = axes[i]  

        # subset network
        network_data = df[df['network'] == network]
        
        # red if wthin, else Set2
        types = network_data['type'].unique()
        palette = {t: 'darkred' if t == 'wthn' else sns.color_palette("Set2", n_colors=len(types))[j]
                   for j, t in enumerate(types)}

        pt.RainCloud(
            x='type', y='value', data=network_data, 
            palette=palette, bw=.4, width_viol=0.8, orient="v", ax=ax
        )
        
        ax.set_title(rf'$\bf{network}$' + f'\nWithin & Between {len(unique_networks)} Network Correlations')
        ax.set_xlabel('')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=90, fontsize=9)
        ax.set_ylabel('Aggregate Edgewise Mean (r)')

    # hide unused frames
    for j in range(len(unique_networks), len(axes)):
        fig.delaxes(axes[j])

    
    plt.savefig(f'{output_dir}/xcpd_{len(unique_networks)}-network-summaries.png')
    plt.close()

else:
    print(f"\t FILE: f'{xcpd_out}/3T_combined-network.tsv' doesnt exist")


if os.path.exists(f'{xcpd_out}/3T_combined-anatfiles-check.tsv'):
    print("Making XCP-D Counts & Freesurfer Plots")
    coldf_names = ["subject","parcel","pear_relmat","rest_runs", "volumes"] + roi_check

    df = pd.read_csv(f'{xcpd_out}/3T_combined-anatfiles-check.tsv', sep='\t', on_bad_lines='skip', 
                     index_col=None, header=None, 
                     names=coldf_names)
    
    n_subs = len(df['subject'].unique())
    exists_percentage = np.round(df['pear_relmat'].value_counts(normalize=True) * 100,3)

    # count 'rest_runs' values
    rest_run_counts = df['rest_runs'].value_counts()
  

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    # Plot 1: XCP-D rest_runs count
    sns.barplot(x=rest_run_counts.index, y=rest_run_counts, ax=ax2, palette='Oranges')
    ax2.set_title(f'Subject n = {n_subs} \n Num Rest Runs')
    ax2.set_ylabel('Count')
    # Plot 2: XCP-P Pearson Corr relmat.tsv exists percentage
    sns.barplot(x=exists_percentage.index, y=exists_percentage, ax=ax1, palette='Blues')
    ax1.set_title(f'Subject n = {n_subs} \n {np.round(exists_percentage.iloc[0],1)}% *_realmat.tsv exits')
    ax1.set_ylabel('%')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/xcpd_counts-pearcorrexist.png')
    plt.close()


    # Plot 3: plot of thickness across regions
    df_melted = df[roi_check].melt(var_name='ROI', value_name='Value')
    plt.figure(figsize=(10, 6))
    
    pt.RainCloud(x='ROI', y='Value', data=df_melted, bw=0.2, width_viol=0.6, orient="h")
    # Set plot title and labels
    plt.title('Free Surfer Cortical Thickness (CT) Estimates Across 5 Shaefer 1000 ROIs')
    plt.xlabel('CT Est.')
    plt.ylabel('ROI')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/xcpd_dist-corthick.png')
    plt.close()

else:
    print(f"\t FILE: f'{xcpd_out}/3T_combined-anatfiles-check.tsv' doesnt exist")



if os.path.exists(f'{output_dir}/brain_corthick-rois.png'):
    print(f"Schaefer ROI img exists, not recreating. \n \t f'{output_dir}/brain_corthick-rois.png")
else:
    print("Schaefer ROI image doesnt exist, creating using n = 1000 nilearn atlas. \n \t f'{output_dir}/brain_corthick-rois.png")
    from nilearn.datasets import fetch_atlas_schaefer_2018
    from nilearn.image import math_img
    from nilearn import plotting

    atlas = fetch_atlas_schaefer_2018(n_rois=1000,resolution_mm=2, yeo_networks=7)

    label_indices = [43, 165, 300, 455, 813]
    n_rows = 6 // 2

    fig, axes = plt.subplots(n_rows, 2, figsize=(10, 4 * n_rows))
    axes = axes.flatten()

    for i, label_index in enumerate(label_indices):
        # multiply by index + 1, since background is 0
        specific_label_mask = math_img(f"img == {label_index + 1}", img=atlas.maps)
        # plot and customize label, removing last axis since it is empty
        plotting.plot_roi(specific_label_mask, display_mode='xz', draw_cross=False, figure=fig, axes=axes[i])
        
        # make black background white + text black
        title_text = f"Label: {atlas.labels[label_index-1]}, index {label_index}"
        axes[i].set_title(title_text, fontsize=9, color='black', backgroundcolor='white', alpha = 1)
        axes[-1].axis('off')

    plt.savefig(f'{output_dir}/brain_corthick-rois.png')
    plt.close()
