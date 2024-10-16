#!/bin/bash

# this group batch takes some times to run as it requiers the BIDS directory and the preprocessed content. 
# Update the mriqc version information, as well as the input BIDS folders and the location of the MRIQC preprocessed output.
# Note: if the BIDS data are on S3 buckets, you will need to reconfigure the below code.

proj_dir=`pwd`
out_dir=${proj_dir}/out_group
mriqc_vr=mriqc_v23_1_0
ses=3T
subs=${proj_dir}/subj_list/${1}
s3_path=s3://hcp-youth/derivatives/mriqc_v23_1_0/ses-${ses}
hcp_dir=s3://HCP_YA/BIDS
singularity=`which singularity`
sif_img=/home/faird/shared/code/external/utilities/mriqc/mriqc_23.1.0rc0.sif

if [ -n $1 ]; then
        filename=$(basename ${subs} .txt)
        mkdir -p ${out_dir}/${filename}
        echo "Naming group output folderbased on filename: ${filename}"
else
        echo "Subjects file path not provided or does not exist, ${subs} "
fi

# set input, work and output paths
bids_dir=/scratch.global/${USER}/${mriqc_vr}/bids_dir_${filename}
mriqc_in=/scratch.global/${USER}/${mriqc_vr}/individual_${filename}
work_dir=/scratch.global/${USER}/${mriqc_vr}/work_dir/group_${filename}

# create working and bids dir
if [ ! -d ${work_dir}/ ]; then
        mkdir -p ${work_dir}/
fi

if [ ! -d ${bids_dir}/ ]; then
        mkdir -p ${bids_dir}/
fi

# interate over subjects, sync from s3 and cp bids data to bids_fir
cat $subs | while read sub ; do
	s3cmd sync --recursive ${s3_path}/sub-${sub}/sub-${sub} ${mriqc_in}/
	for folder in fmap anat func ; do
		mkdir -p ${bids_dir}/sub-${sub}/ses-${ses}/${folder} 
		s3cmd sync --recursive --exclude="*/dwi/*" ${hcp_dir}/sub-${sub}/ses-${ses}/${folder}/ ${bids_dir}/sub-${sub}/ses-${ses}/${folder}/
	done
done

cp ${proj_dir}/../dataset_description.json ${bids_dir}

# run group mriqc
singularity run --cleanenv \
-B ${bids_dir},${mriqc_in},${work_dir} \
${sif_img} \
${bids_dir} ${mriqc_in} group \
-vv \
-w ${work_dir}

# copy group estimates from mriqc_output then delete bids_dir/work_dir/mriqcinfo
cp ${mriqc_in}/group* ${out_dir}/${filename}/

cat $subs | while read sub ; do
	rm -r ${bids_dir}/sub-${sub}*
	rm -r ${work_dir}/*
	rm -r ${mriqc_in}/sub-${sub}*
done

