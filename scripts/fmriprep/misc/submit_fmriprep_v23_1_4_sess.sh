#!/bin/bash -l

array=$1

if [ -z "$array" ]

then
      echo ""
      echo "No job array specified! Please enter jobs to run as argument:"
      echo ""
      echo "    EXAMPLE 1:  submit_ALL.sh 0-99"
      echo "    EXAMPLE 2:  submit_ALL.sh 1-3,6,9"
      echo ""

else
      echo "Please choose a value baselineYear1Arm1 or 2YearFollowUpYArm1:"
      read ses

      echo ""
      echo "Submitting the following jobs for fMRIprep 23.1.4 processing now: $array"
      echo ""

      fmriprep_abcd=$(sbatch --parsable -a $array resources_fmriprep_v23_1_4_${ses}.sh )
      echo "fmriprep_v23_1_4 JOB ID: $fmriprep_abcd"

      echo ""
      echo "Use 'squeue -al --me' to monitor jobs."
      echo ""
fi

