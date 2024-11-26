# ABCD-BIDS: XCP-D Post-processing Pipeline

This code is to run [XCP-D](https://xcp-d.readthedocs.io/en/latest/)] Post-processing. As described in [Mehta et al., 2024](https://doi.org/10.1162/imag_a_00257), XCP-D is a robust package for post-processing fMRI data, particularly resting state data. The software addresses the variability and reproducibility issues in existing in exist workflows in the field of fMRI. XCP-D supports multiple pre-processed formats: fMRIPrep, HCP and ABCD-BIDS. This allows application of denoising strategies across a range of datasets. It software is a collaborative effort between [PennLINC](https://www.pennlinc.io/) and the [CDNI](https://innovation.umn.edu/developmental-cognition-and-neuroimaging-lab/) lab, it features a modular Python codebase, integration with infant-fMRIPrep, and adherence to BIDS conventions. XCP-D introduces advanced features like surface-based analysis with CIFTI workflows, expanded quality measures, and detailed visual reports, ensuring stability through extensive CI testing. Distributed via Docker and Apptainer, XCP-D streamlines post-processing for reproducible and generalizable neuroimaging research.

The general overview:

- template.fmriprep
    - This is the template used to copy data to a tmp area to preprocess locally. It also includes the singularity run for XCP-D + the sync to s3
- resources_*.sh 
    - This is your research request for each XCP-D job that is submitted to slurm (takes 2-5hrs each)
- submit_*.sh 
    - jobs are submitted using arrays indicating the runs in `run_files.*` folder
    - to submit the first 100 subjs for independent slurm jobs use: ./submit_xcpd.sh 0-100

The XCP-D pile here only focuses on the `resting state` data and does not postprocess the task fMRI data. Note, teh [post-scrubbing threshold](https://xcp-d.readthedocs.io/en/latest/usage.html#:~:text=Default%3A%20auto-,%2D%2Dmin%2Dtime,-%2C%20%2D%2Dmin_time) is set to `0` due to issues related to not enough low-motion data in a run that is being concatenated (The default minimum is 4-minute, resulting in error: ValueError: QCPlots requires a value for input 'bold_file').

The singularity run is currently templated as:

```bash
singularity run --cleanenv \
    -B "${fmriprep_dir}:/fmriprep_dir" \
    -B "${data_dir}/processed/${xcpd_ver}/sub-${subj_id}_ses-${ses_id}:/output_dir" \
    -B "${data_dir}/work_dir/${xcpd_ver}/sub-${subj_id}_ses-${ses_id}:/wd" \
    -B "${freesurfer_license}:/opt/freesurfer/license.txt " \
    "${singularity_img}" \
    /fmriprep_dir /output_dir participant \
    --mode abcd \
    -m \
    --participant-label ${subj_id} \
    --task-id rest \
    --nthreads 8 \
    --omp-nthreads 3 \
    --mem-gb 100 \
    --min-time 0 \
    --lower-bpf 0.009 \
    --motion-filter-type notch --band-stop-min 12 --band-stop-max 18 \
    --clean-workdir \
    -vv \
    -w /wd

```

## XCP-D Automated QC

TBD

