#!/bin/bash -l
#SBATCH -J fp_v23_2YearFollowUpYArm1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=12
#SBATCH --mem-per-cpu=8G
#SBATCH --tmp=400gb
#SBATCH -t 18:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=mdemiden@umn.edu
#SBATCH -p msismall,agsmall#amdsmall
#SBATCH -o fp_2YearFollowUpYArm1_logs/%x_%A_%a.out
#SBATCH -e fp_2YearFollowUpYArm1_logs/%x_%A_%a.err
#SBATCH -A feczk001 #faird

cd run_files.fmriprep_v23_1_4_2YearFollowUpYArm1

module load singularity
file=run${SLURM_ARRAY_TASK_ID}

bash ${file}
