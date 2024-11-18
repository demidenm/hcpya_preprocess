#!/bin/sh
#SBATCH -J fp_v23_3T
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=12
#SBATCH --mem-per-cpu=8GB
#SBATCH --tmp=650gb
#SBATCH -t 38:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=mdemiden@umn.edu
#SBATCH -p msismall,agsmall#amdsmall
#SBATCH -o fmriprep_3T_logs/%x_%A_%a.out
#SBATCH -e fmriprep_3T_logs/%x_%A_%a.err
#SBATCH -A feczk001 #faird

cd fsrerun.fmriprep_v24_0_1_3T

module load singularity
file=run${SLURM_ARRAY_TASK_ID}

bash ${file}
