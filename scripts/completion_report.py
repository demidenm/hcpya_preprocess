import os
import pandas as pd
import subprocess
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# set folders
input_dir = './'
tmp = './tmp'
output_dir = '../imgs'
grp_fold = './mriqc/group_mriqc/out_group'
qc_out = './fmriprep/post_preprocessing_checks/qc_sdc-similarity'

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

# Create Complete plots for FMRIPrep / MRIQC / XCP-D
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

# Create Summary Plots of Group Derivatives MRIQC

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
        
    columns_to_plot = plot_metrics[img_key]
    sess_list = list(df['session'].unique())

    # convert mriqc to numeric if not all ready
    for col in columns_to_plot:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # size dependenint on colums * sessions
    plt.figure(figsize=(12 * len(sess_list), len(columns_to_plot) * 5))

    for i, col in enumerate(columns_to_plot):
        for j, sess in enumerate(sess_list):
            plt.subplot(len(columns_to_plot), len(sess_list), i * len(sess_list) + j + 1)  # Create subplot grid
            
            # filter for session and plot each metrics
            df_session = df[df['session'] == sess]
            
            # boxplot for the current session and metric
            sns.boxplot(x='task_names', y=col, hue='run', data=df_session)
            
            if j == 0:
                plt.ylabel(col.upper(), fontsize=12)
            plt.title(f'Ses: {sess} - {col.upper()}', fontsize=14, fontweight='bold')
            plt.xticks(rotation=45)
            plt.xlabel("")
            plt.legend(title='Run', bbox_to_anchor=(1.01, 0.5), loc='center left', borderaxespad=0.)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/{img_key}_mriqc-plot.png')
    plt.close() 


# summaries peristimulus plots
if os.path.exists(f'{qc_out}/3T_check-peristim.tsv'):
    print("Making Peristimulus Summary Plots")
    peristim_df = pd.read_csv(f'{qc_out}/3T_check-peristim.tsv', sep = '\t', 
                              names=['sub','sess','task','region','peak_tr','peak_mean', 'peak_se']).drop_duplicates(subset='sub')
    peri_sub_n = len(peristim_df)
    # make plot
    sns.set(style="whitegrid")
    fig, axes = plt.subplots(1, 3, figsize=(15, 10))  # 1 row, 3 columns

    # Define custom y-axis labels for each column
    y_labels = {
        'peak_tr': "Peak TR",
        'peak_mean': "Mean Signal at Peak",
        'peak_se': "SE Signal at Peak"
    }

    # columns and colors 
    columns_of_interest = ['peak_tr', 'peak_mean', 'peak_se']
    colors = sns.color_palette("Set2", len(columns_of_interest))

    for ax, col, color in zip(axes, y_labels.keys(), colors):
        # violin plot
        sns.violinplot(data=peristim_df, y=col, ax=ax, color=color, inner=None, alpha=0.6, cut=0)
        # strip plot points
        sns.stripplot(data=peristim_df, y=col, ax=ax, color='gray', jitter=0.5, alpha=0.6)
        
        ax.set_ylabel(y_labels[col])  # Use the custom label
        ax.set_xlabel("")  

        # expand min/max to avoid weird cut-offs
        ax.set_ylim(peristim_df[col].min() - 0.5, peristim_df[col].max() + 0.5)

    plt.subplots_adjust(wspace=0.5)  # Adjust horizontal spacing between plots
    plt.suptitle(f'Max TR (.720sec) from Peristimulus Plots across N = {peri_sub_n}', fontsize=14)
    plt.savefig(f'{output_dir}/peristim_distributions.png')
    plt.close() 
else:
    print(f'\tFILE: \n{qc_out}/3T_check-peristim.tsv doesnt exist')

# summaries qc-similarity estimates and fmriprep reports
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
