#!/bin/bash

# this group batch takes some times to run as it requiers the BIDS directory and the preprocessed content. 
# Update the mriqc version information, as well as the input BIDS folders and the location of the MRIQC preprocessed output.
# Note: if the BIDS data are on S3 buckets, you will need to reconfigure the below code.

path=`pwd`
mriqc_vr=mriqc_v23_1_0
dir=${path}/..
data_out=${dir}/group_out
ses=baselineYear1Arm1
#ses=2YearFollowUpYArm1
subs=${dir}/group_mriqc/${1}

if [ -n $1 ]; then
        filename=$(basename ${subs} .txt)
        mkdir ${path}/${filename}
        echo "Naming group output folderbased on filename: ${filename}"
else
    	echo "Subjects file path not provided or does not exist, ${subs} "
fi

# set input, work and output paths
s3_path=s3://ABCD_BIDS/derivatives/mriqc_v23_1_0/ses-${ses}
abcd_dir=/spaces/ngdr/ref-data/abcd/nda-3165-2020-09
bids_dir=/scratch.global/${USER}/${mriqc_vr}/bids_dir_${filename}
mriqc_in=/scratch.global/${USER}/${mriqc_vr}/individual_${filename}
work_dir=/scratch.global/${USER}/${mriqc_vr}/work_dir/group_${filename}
# set singuarlity
singularity=`which singularity`
sif_img=/home/faird/shared/code/external/utilities/mriqc/mriqc_23.1.0rc0.sif

if [ -n $1 ]; then
	filename=$(basename ${subs} .txt)
    	mkdir ${path}/${filename}
	echo "Naming group output folderbased on filename: ${filename}"
else
	echo "Subjects file path not provided or does not exist, ${subs} "
fi

# create working and bids dir
if [ ! -d ${work_dir}/ ]; then
        mkdir -p ${work_dir}/
fi

if [ ! -d ${bids_dir}/ ]; then
        mkdir -p ${bids_dir}/
fi

# interate over subjects, sync from s3 and cp bids data to bids_fir
cat $subs | while read sub ; do
	s3cmd sync --recursive ${s3_path}/sub-${sub} ${mriqc_in}/
	for folder in fmap anat func ; do
		mkdir -p ${bids_dir}/sub-${sub}/ses-${ses}/${folder} 
		cp ${abcd_dir}/sub-${sub}/ses-${ses}/${folder}/* ${bids_dir}/sub-${sub}/ses-${ses}/${folder}/
	done
done

cp ${dir}/dataset_description.json ${bids_dir}

# run group mriqc
singularity run --cleanenv \
-B ${abcd_dir},${bids_dir},${mriqc_in},${work_dir} \
${sif_img} \
${bids_dir} ${mriqc_in} group \
-vv \
-w ${work_dir}

# copy group estimates from mriqc_output then delete bids_dir/work_dir/mriqcinfo
cp ${mriqc_in}/group* ${path}/${filename}/

rm -r ${bids_dir}
rm -r ${work_dir}
# below wont work, too many  files in argument
rm -r ${mriqc_in}

