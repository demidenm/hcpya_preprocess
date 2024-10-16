#!/bin/bash -l
#SBATCH -J mriqc_grp_base
#SBATCH --array=1,8-10#4-7 #1-3 # 8-10
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=10
#SBATCH --mem-per-cpu=8G
#SBATCH --tmp=200gb
#SBATCH -t 05:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=mdemiden@umn.edu
#SBATCH -p msismall,agsmall
#SBATCH -o mriqc_grp_logs/mriqc_%A_%a.out
#SBATCH -e mriqc_grp_logs/mriqc_%A_%a.err
#SBATCH -A feczk001 #faird


module load singularity

file=run_grp.sh
id=${SLURM_ARRAY_TASK_ID}
bash ${file} subjects_${id}.txt
