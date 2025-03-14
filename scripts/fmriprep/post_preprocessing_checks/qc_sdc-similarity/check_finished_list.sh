#!/bin/bash 

mkdir -p tmp 
run_file_dir="./run_files.3T"
cat ../../3T_completed.tsv | awk -F" " '{ print $1 }' | sort | uniq > ./tmp/completed_values.txt
cat 3T_check-html-similarity.tsv | awk -F" " '{ print $1 }' | sort | uniq > ./tmp/check_values.txt

cat 3T_check-html-similarity.tsv | awk -F" " '{ print $1 }' | sort | uniq > ./tmp/check_values.txt

echo "Checking subjects that completed fMRIPrep but are not in *_similarity.tsv"
for sub in `grep -Fxv -f ./tmp/check_values.txt ./tmp/completed_values.txt` ; do 
	value=`grep -l "sub=${sub}" "$run_file_dir"/* 2>/dev/null | awk -F"/" '{ print $3 }'`
	echo -e "\tRerun: ${value}"
done

