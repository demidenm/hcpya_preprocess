#!/bin/bash 
output_type=mriqc_v23_1_0
data_bucket="s3://ABCD_BIDS" # bucket to input data onto s3, preprocessed output pushed to
run_folder=`pwd`

echo "Please choose a value baselineYear1Arm1 or 2YearFollowUpYArm1:"
read ses

if [ -n "${ses}" ]; then
    if [[ "$ses" == "baselineYear1Arm1" || "$ses" == "2YearFollowUpYArm1" ]]; then
        echo "${ses} chosen as ses, continuing."
    else
        echo
        echo "should be baselineYear1Arm1 or 2YearFollowUpYArm1, provided ${ses}. Exiting."
        echo
        exit 1
    fi

else
        echo
        echo "Variable is empty, expected: baselineYear1Arm1 or 2YearFollowUpYArm1. Exiting"
        echo
        exit 1

fi

path_subjs=${run_folder}/../../subj_list/subjs_${ses}.tsv 

s3cmd ls s3://ABCD_BIDS/derivatives/${output_type}/ses-${ses}/ | awk -F'/' '{ print $7 }' > s3_${ses}_filesfolders.txt

uniq_folds=$(cat ./s3_${ses}_filesfolders.txt | grep -Ev '\.html$|\.bidsignore$|\.json$|\.tsv$' | wc -l )
cat ./s3_${ses}_filesfolders.txt | grep -Ev '\.html$|\.bidsignore$|\.json$|\.tsv$' > s3_${ses}_subfolders.txt

echo "On s3 in ${ses}"
echo -e "\t Unique subject folders: $uniq_folds "


# check diff
completed_subs=../mriqc_${ses}_completed.csv
comp_list=./${output_type}_completed.txt
truncate -s 0 $comp_list

cat $completed_subs | while read line ; do
	sub=$(echo $line | awk -F' ' '{ print $1 }' )
	echo "sub-${sub}" >> $comp_list
done

# check how many files in completed list are not in the s3 list (note: fitler repeating/irrelevant files)
grep -v -F -f ./s3_${ses}_subfolders.txt $comp_list > ./${output_type}_${ses}_subsmiss_s3.txt

s3_missing=$(cat ./${output_type}_${ses}_subsmiss_s3.txt | wc -l )
echo
echo "Subjects not sync'd onto s3://ABCD_BIDS/derivatives/${output_type}/ses-${ses}"
echo -e "\t Number: $s3_missing "

echo -e "subject\trun_num" > ./s3_${ses}_runinfo.txt

cat ${output_type}_${ses}_subsmiss_s3.txt | while read sub ; do
	sub_r=$(echo $sub | awk -F"-" '{ print $2 }')
	order_num=$(grep -n $sub_r ${path_subjs} | awk -F":" '{ print $1}' )
	run_num=$((order_num - 1))
	echo -e "${sub_r}\t${run_num}" >> ./s3_${ses}_runinfo.txt 
done
