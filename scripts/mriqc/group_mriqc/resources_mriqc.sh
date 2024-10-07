#!/bin/bash -l
#SBATCH -J mriqc_grp_base
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=12
#SBATCH --mem-per-cpu=6G
#SBATCH -t 24:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=mdemiden@umn.edu
#SBATCH -p msismall,agsmall#,amdsmall
#SBATCH -o mriqc_grp_logs/mriqc_%A_%a.out
#SBATCH -e mriqc_grp_logs/mriqc_%A_%a.err
#SBATCH -A feczk001 #faird


module load singularity

file=run_grp

bash ${file} ${1}
