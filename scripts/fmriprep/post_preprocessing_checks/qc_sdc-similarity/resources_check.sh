#!/bin/bash -l
#SBATCH -J check_fpout
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=6
#SBATCH --mem-per-cpu=8G
#SBATCH -t 03:00:00
#SBATCH --tmp=200g
#SBATCH --mail-type=ALL
#SBATCH --mail-user=mdemiden@umn.edu
#SBATCH -p msismall,amdsmall#agsmall#amdsmall
#SBATCH -o check_logs/%x_%A_%a.out
#SBATCH -e check_logs/%x_%A_%a.err
#SBATCH -A feczk001 #faird

#source $HOME/miniconda3/etc/profile.d/conda.sh
#source /home/faird/mdemiden/miniconda3/etc/profile.d/conda.sh
#conda activate fmri_env

module load fsl 
module load freesurfer 
cd run_files.${1}
file=run${SLURM_ARRAY_TASK_ID}
bash ${file}
