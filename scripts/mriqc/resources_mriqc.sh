#!/bin/bash -l
#SBATCH -J mriqc_v23_SESS
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=80G
#SBATCH --tmp=375gb
#SBATCH -t 02:30:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=mdemiden@umn.edu
#SBATCH -p msismall,agsmall#agsmall # amdsmall
#SBATCH -o mriqc_SESS_logs/mriqc_%A_%a.out
#SBATCH -e mriqc_SESS_logs/mriqc_%A_%a.err
#SBATCH -A feczk001 #faird # feczk001

module load singularity

cd run_files.mriqc_v23_1_0_SESS
file=run${SLURM_ARRAY_TASK_ID}
bash ${file}
