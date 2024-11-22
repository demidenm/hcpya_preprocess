#!/bin/bash -l
#SBATCH -J xcpd_3T
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8GB
#SBATCH --tmp=250gb
#SBATCH -t 10:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=mdemiden@umn.edu
#SBATCH -p msismall,agsmall
#SBATCH -o xcp_d_3T_logs/%x_%A_%a.out
#SBATCH -e xcp_d_3T_logs/%x_%A_%a.err
#SBATCH -A feczk001 #faird

cd run_files.xcpd_v0_9_0_3T

module load matlab/R2019a
module load singularity
file=run${SLURM_ARRAY_TASK_ID}

bash ${file}
