#! /bin/bash

# Compared completion of preprocessing of subjects/sessions and the modifications to data on NGDR.
# Creating list to preprocess, as needed.

# Setting Variables: $ngdr_inp ngdr data path and $dir the current directory path.
# User Input: session value (baselineYear1Arm1 or 2YearFollowUpYArm1). Validates that correct option 
# Checks if $finished_file from preprocessing existss
# Fach line (subject) of the $file $finished_file 
# 	Checks if $sub from $finished_file matches subjectes in  $subjs_ignore. If yes, skips subect
#	Retrieves date of modified folder for subj/session at ngdr_inp and data preprocessed from finished
# Creates datas and then compares system (%s) timestamps
#	If fp is older than ngdr, it increments a counter and prints a message indicating that fp is older than ngdr.
#	If fp is newer than ngdr, it continues to the next subject.
#	If there's an error or the dates are equal, it prints an error message.
#
# Written: Michael Demidenko, April 2024


ngdr_inp="/spaces/ngdr/ref-data/abcd/nda-3165-2020-09"
dir=$(pwd)

echo "Please choose a value baselineYear1Arm1 or 2YearFollowUpYArm1:"
read ses

if [[ "$ses" == "baselineYear1Arm1" || "$ses" == "2YearFollowUpYArm1" ]]; then
    echo "${ses} chosen as ses, continuing."
else
    echo "should be baselineYear1Arm1 or 2YearFollowUpYArm1, provided ${ses}. Exiting."
    exit 1
fi

subjs_ignore=${dir}/../../subj_list/fix_dwi_${ses}.txt
subjs_list=${dir}/../../subj_list/subjs_${ses}.txt
finished_file="${dir}/../../${ses}_completed.tsv"
out_runs=${dir}/${ses}_rerun-sbatch.txt
truncate -s 0 $out_runs # run as new each time

if [ ! -f "$finished_file" ]; then
    echo "File $finished_file not found. Exiting."
    exit 1
fi

counter=0
cat ${finished_file} | awk -F" " '{print $1 }' | while read sub ; do
	if grep -q "^$sub$" "${subjs_ignore}"; then
		#echo "Skipping $sub . Found in ignore file: ${subjs_ignore}"
		continue
	fi
	
	fp=$(cat $finished_file | grep $sub | awk -F" " '{ print $5,$6,$9 }' ) 
	ngdr=$(ls ${ngdr_inp}/sub-${sub} --full-time | grep "${ses}" \
		| awk '{print $6}' | xargs -I {} date -d {} +"%b %d %Y")

	if [ -z "$fp" ] || [ -z "$ngdr" ]; then
		echo "Error: Couldn't retrieve dates for $sub ($fp / $ngdr). Check file, skipping."
		continue
	fi

	ngdr_timestamp=$(date -d "$ngdr" +"%s") # s = system
	fp_timestamp=$(date -d "$fp" +"%s")
	
	if [ "$fp_timestamp" -lt "$ngdr_timestamp" ]; then	
		((counter++))
		sub_run=$(cat ${subjs_list} | grep -n "${sub}" | awk -F":" '{ print $1 - 1 }') 
		echo "${counter}. ${sub} (run #: $sub_run ) -- $fp (${fp_timestamp}) is OLDER than $ngdr (${ngdr_timestamp}) "
		echo -e "${sub}\t${sub_run}" >> ${out_runs}

	elif [ "$fp_timestamp" -gt "$ngdr_timestamp" ]; then
		#echo "$fp is newer than $ngdr "
		continue
	else
		echo "${sub}: Error with dates $fp and/or $ngdr"
	fi
done

echo
rerun_n=$(cat $out_runs } | wc -l )
echo "There are a list of $rerun_n subjects to rerun for $ses "
echo

