import numpy as np
import os
from pyrelimri import masked_timeseries
from glob import glob
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import ptitprince as pt  
import concurrent.futures
import argparse
import matplotlib
matplotlib.use('Agg')


parser = argparse.ArgumentParser(description="Script to run similarity estimate between func/anat masks")
parser.add_argument("--in_dir", help="directory with subjects data to BOLD and sourcedata path to events")
parser.add_argument("--sub_id", help="subject ID, without prefix 'sub-'")
parser.add_argument("--tmp_out", help="task label. In HCP using 'motor'", default='motor')
parser.add_argument("--parcel_name", help="XCP-D parcel name e.g. 4S1056Parcels, HCP, Gordon, default = 4S1056Parcels", default='4S1056Parcels')


# parse input args
args = parser.parse_args()
sub_id = args.sub_id
parcel_name = args.parcel_name
input_dir = args.in_dir
tmp_out=args.tmp_out
roi_check=['LH_Vis_43', 'LH_SomMot_84', 'LH_Limbic_OFC_12', 'LH_Default_PFC_40', 'RH_Limbic_OFC_1']


def clean_sort_xcpd_pearcorr(path_pearcorr_xcp, round_dec_corr: int = 2):
    xcpd_pearcorr = round(
        pd.read_csv(path_pearcorr_xcp, sep = '\t'),
        round_dec_corr
    )
    
    url = "https://raw.githubusercontent.com/PennLINC/AtlasPack/main/atlas-4S1056Parcels_dseg.tsv"
    networks_df = pd.read_csv(url, sep='\t')
    
    # link label to nework
    map_label_to_network = dict(zip(networks_df['label'], networks_df['network_label_17network']))
    
    # drop node (row label of roi) and remap label names to associated network
    pear_corr_clean = xcpd_pearcorr.drop(columns=['Node'])
    pear_corr_clean.columns = pear_corr_clean.columns.map(map_label_to_network)
    
    # some matrix result in NaN if empty, fill with 0
    pear_corr_clean = pear_corr_clean.fillna(0)

    # index is same order as columns, label accordingly
    pear_corr_clean.index = pear_corr_clean.columns

    # some labels dont belong to networks, mapping results in 'NaN', drop non-network columns
    pear_corr_clean = pear_corr_clean.loc[:, ~pear_corr_clean.columns.isna()]
    pear_corr_clean = pear_corr_clean.loc[~pear_corr_clean.index.isna()]
        
    return pear_corr_clean.sort_index(axis=0).sort_index(axis=1)


def extract_subj_values(sub, global_dir, parcel):
    subject_results = []
    
    try:
        # Define the path to the correlation matrix file
        corr_path = f'{global_dir}/sub-{sub}/ses-3T/func/sub-{sub}_ses-3T_task-rest_space-fsLR_seg-{parcel}_stat-pearsoncorrelation_relmat.tsv'
        
        # Assuming `clean_sort_xcpd_pearcorr()` is a function that returns the sorted and cleaned correlation matrix
        pear_corr_sorted = clean_sort_xcpd_pearcorr(corr_path, 2)
        
        # Get the unique network names from the correlation matrix columns
        network_names = pear_corr_sorted.columns.unique()
        
        # Initialize a list to store individual subject data

        for network in network_names:
            # Get indices for the current network
            network_indices = pear_corr_sorted.columns[pear_corr_sorted.columns == network]
            
            # Compute within-network average
            within_matrix = pear_corr_sorted.loc[network_indices, network_indices]
            within_values = within_matrix.values
            within_avg = np.mean(within_values[np.triu_indices(len(network_indices), k=1)])  # Upper triangle excluding diagonal
            
            # Store within-network result
            subject_results.append({
                'subject': f'sub-{sub}',
                'network': network,
                'type': 'wthn',
                'value': within_avg
            })
            
            # Compute between-network averages
            for other_network in network_names:
                if other_network != network:
                    other_indices = pear_corr_sorted.columns[pear_corr_sorted.columns == other_network]
                    between_matrix = pear_corr_sorted.loc[network_indices, other_indices]
                    between_avg = between_matrix.values.mean()
                    
                    # Store between-network result
                    subject_results.append({
                        'subject': f'sub-{sub}',
                        'network': network,
                        'type': f'btwn_{other_network}',
                        'value': between_avg
                    })
        
        return subject_results
    
    except Exception as e:
        print(f"Error processing subject {sub}: {e}")
        subject_results.append({
                'subject': f'sub-{sub}',
                'network': "no_r_mat",
                'type': "no_r_mat",
                'value': None
            })
        return subject_results



network_results = pd.DataFrame(extract_subj_values(sub=sub_id, global_dir=input_dir, parcel=parcel_name))
network_results.to_csv(f'{tmp_out}/network_{sub_id}.tsv', sep = '\t', index=False)


# extract anat / file info
try:
    if os.path.exists(f'{input_dir}/sub-{sub_id}/ses-3T/func/sub-{sub_id}_ses-3T_task-rest_space-fsLR_seg-{parcel_name}_stat-pearsoncorrelation_relmat.tsv'):
        cb_bold = pd.read_csv(f'{input_dir}/sub-{sub_id}/ses-3T/func/sub-{sub_id}_ses-3T_task-rest_space-fsLR_seg-{parcel_name}_stat-mean_timeseries.tsv', sep='\t')
        pear_corr = 'exists'
    else:
        cb_bold = pd.read_csv(f'{input_dir}/sub-{sub_id}/ses-3T/func/sub-{sub_id}_ses-3T_task-rest_dir-RL_run-1_space-fsLR_seg-{parcel_name}_stat-mean_timeseries.tsv', sep = '\t')
        pear_corr = 'none'
except:
    cb_bold = None
    pear_corr = 'none'

runs = len(glob(f'{input_dir}/sub-{sub_id}/ses-3T/func/sub-{sub_id}_ses-3T_task-rest_dir-*_run-*_space-fsLR_seg-{parcel_name}_stat-mean_timeseries.tsv'))

anat_file = glob(f'{input_dir}/sub-{sub_id}/ses-3T/anat/sub-{sub_id}_ses-3T*_space-fsLR_seg-{parcel_name}_stat-mean_desc-thickness_morph.tsv')[0]
thick_t1 = pd.read_csv(anat_file, sep='\t')


data = {
'sub': f'sub-{sub_id}',
'parcel': parcel_name,
'realmat_exists': pear_corr,
'rest_runs': runs,
'rest_vols': "no rest" if cb_bold is None else len(cb_bold)
}

# relevant ROI data 
for roi in roi_check:
    data[roi] = thick_t1[roi].iloc[0]

# DataFrame with one row
anat_file_info = pd.DataFrame([data])
anat_file_info.to_csv(f'{tmp_out}/anat-files_{sub_id}.tsv', sep = '\t', index=False)
