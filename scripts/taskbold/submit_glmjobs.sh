#!/bin/bash -l
#SBATCH -J hcp_glms
#SBATCH --array=113#169,171,991,1019,441,113,1087
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=60GB
#SBATCH --tmp=200gb
#SBATCH -t 10:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=mdemiden@umn.edu
#SBATCH -p msismall,agsmall#amdsmall
#SBATCH -o logs/%x_%A_%a.out
#SBATCH -e logs/%x_%A_%a.err
#SBATCH -A feczk001 #faird

cd glmruns.3T

module load singularity
file=run${SLURM_ARRAY_TASK_ID}

bash ${file}
