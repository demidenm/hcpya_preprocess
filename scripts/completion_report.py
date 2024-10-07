import os
import pandas as pd
import subprocess
import matplotlib.pyplot as plt
import seaborn as sns


input_dir = './'
output_dir = '../imgs'
os.makedirs(output_dir, exist_ok=True)

# specify preproc types
folders = ['mriqc', 'fmriprep']

# dictionary to get data for completion outputs
subject_counts = {}

for preproc_type in folders:
    subject_counts[preproc_type] = {}
    folder = os.path.join(input_dir, preproc_type)    
    
    # each .tsv file in the preproc folders
    for filename in os.listdir(folder):
        if filename.endswith('.tsv'):
            session, status = filename.split('_')[:2]
            filepath = os.path.join(folder, filename)
            # create tmp for first sub column to avoid parsing errors
            tmp_file = f'{output_dir}/subs_{preproc_type}_{session}{status}.tsv'
            subprocess.run(f"awk '{{ print $1 }}' {filepath} > {tmp_file}", shell=True, check=True)
            subj_count = len(pd.read_csv(tmp_file, header=None)[0].unique())

            if session not in subject_counts[preproc_type]:
                subject_counts[preproc_type][session] = {}
            subject_counts[preproc_type][session][status] = subj_count

# Convert dictionary to a pandas DataFrame
data = []
for preprocessing_type, sessions in subject_counts.items():
    for session, statuses in sessions.items():
        for status, count in statuses.items():
            data.append([preprocessing_type, session, status.replace('.tsv', ''), count])
df = pd.DataFrame(data, columns=['Type', 'Session', 'Status', 'Count'])

sns.set(style="whitegrid")

for preprocessing_type, group_data in df.groupby('Type'):
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