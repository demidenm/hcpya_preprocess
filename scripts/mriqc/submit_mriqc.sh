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
      echo "Please choose a value 3T or 7T:"
      read ses

      echo ""
      echo "Submitting the following jobs for MRIQC processing now: $array"
      echo ""

      sed "s/SESS/${ses}/g" resources_mriqc.sh > ./tmp/tmp_resources_submit_${array}.sh
      miqrc_abcd=$(sbatch --parsable -a $array ./tmp/tmp_resources_submit_${array}.sh )
      echo "mriqc JOB ID: $mirqc_abcd"

      echo ""
      echo "Use 'squeue -al --me' to monitor jobs."
      echo ""
fi

