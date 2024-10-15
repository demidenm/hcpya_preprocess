#!/bin/bash -l
#SBATCH -J fmrip_SESS
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=8G
#SBATCH --tmp=400gb
#SBATCH -t 15:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=mdemiden@umn.edu
#SBATCH -p msismall,agsmall#amdsmall
#SBATCH -o SESS_logs/%x_%A_%a.out
#SBATCH -e SESS_logs/%x_%A_%a.err
#SBATCH -A feczk001 #faird

cd rerunfiles.fmriprep_SESS

module load singularity
file=run${SLURM_ARRAY_TASK_ID}

bash ${file}
