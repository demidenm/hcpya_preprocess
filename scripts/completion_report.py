import os
import pandas as pd
import subprocess
import matplotlib.pyplot as plt
import seaborn as sns
from numpy import np


input_dir = './scripts'
output_dir = './imgs'
grp_fold = './scripts/mriqc/group_mriqc/output'

os.makedirs(output_dir, exist_ok=True)

plot_metrics = {
    'bold': ['fd_mean', 'fwhm_avg', 'snr', 'tsnr'],
    'T1w': ['cnr', 'fwhm_avg','snr_total'],
    'T2w': ['cnr', 'fwhm_avg','snr_total']
}

# specify preproc types & data dict
folders = ['mriqc', 'fmriprep']

subject_counts = {}

for preproc_type in folders:
    subject_counts[preproc_type] = {}
    folder = os.path.join(input_dir, preproc_type)    
    if os.path.exists(folder):
        # each .tsv file in the preproc folders
        for filename in os.listdir(folder):
            if filename.endswith('.tsv'):
                session, status = filename.split('_')[:2]
                filepath = os.path.join(folder, filename)
                # create tmp for first sub column to avoid parsing errors
                tmp_file = f'{output_dir}/subs_{preproc_type}_{session}{status}'
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

for preprocessing_type, group_data in df.groupby('Type'):
    print(preprocessing_type, group_data)
    plt.figure(figsize=(8, 6))
    ax = sns.barplot(x='Status', y='Count', hue='Session', data=group_data, palette='Set3')
    
    plt.title(preprocessing_type)
    plt.xlabel('Completion Status')
    plt.ylabel('N Completed')
    
    # add labels to top
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='bottom', 
                    fontsize=10, color='black', 
                    xytext=(0, 5), 
                    textcoords='offset points')
    plt.savefig(f'{output_dir}/{preprocessing_type}_subject_counts.png')
    plt.close() 


# create summary plots
for img_key in plot_metrics.keys():
    pull_cols = plot_metrics[img_key]
    pull_cols = ['bids_name'] + plot_metrics[img_key]
    df = pd.read_csv(f'{grp_fold}/group_{img_key}.tsv', sep='\t', usecols=pull_cols)
    
    if img_key == 'bold':
        df['session'] = df['bids_name'].str.split('_').str[1].str.split('-').str[1]
        df['task_names'] = df['bids_name'].str.split('_').str[2].str.split('-').str[1]
        df['run'] = np.where(df['bids_name'].str.split('_').str[3].str.split('-').str[0] == 'run',
                        df['bids_name'].str.split('_').str[3].str.split('-').str[1], '01')
    else:
        df['session'] = df['bids_name'].str.split('_').str[1].str.split('-').str[1]
        df['task_names'] = df['bids_name'].str.split('_').str[2]
        df['run'] = np.where(df['bids_name'].str.split('_').str[3].str.split('-').str[0] == 'run',
                             df['bids_name'].str.split('_').str[3].str.split('-').str[1], '01')
        
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
