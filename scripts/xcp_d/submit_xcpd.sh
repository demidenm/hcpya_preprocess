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
#      echo "Please choose a value 3T or 7T:"
#      read ses

      echo ""
      echo "Submitting the following jobs for XCP-D processing now: $array"
      echo ""

      xcpd_hcp=$(sbatch --parsable -a $array ./resources_xcpd.sh )
      echo "XCP-D v0.9.0 JOB ID: $xcpd_hcp"

      echo ""
      echo "Use 'squeue -al --me' to monitor jobs."
      echo ""
fi

