# HCP-YA Task BOLD Modeling

## Summary of Task Modeling Decisions

Task GLMs were fit for all seven of the HCP tasks using the [fMRIPrep](../fmriprep/) derived MNI152 BOLD and the computed [behavioral events](../taskevents/) files. The summaries below include the model examples and counts of subjects ran for the first and second level models.

General information about subject-level models: Within-run and within-subject models were estimated using Nilearn 0.10.4 [Abraham et al., 2014] in Python 3.9.7. FirstLevel models were computed only if subject-level run data had sufficient brain coverage. To ensure sufficient BOLD coverage in MNI space, a Dice coefficient was calculated to assess the overlap between the binarized `MNI152NLin2009cAsym_res-02` brain template and the subject-specific brain mask derived from the BOLD data. The subject's brain mask was retrieved from the fMRIPrep'd preprocessed data. The Dice coefficient between this brain mask and the reference brain mask (from the standard MNI space) was computed using the image_similarity function in `PyReliMRI`. If coverage was < 70% between the two masks, the first level computation was skipped. This ensured that only valid runs with accurate brain masks were included in the first-level GLM fitting.

For each of the two runs with >70% Dice coefficient, a within-run model was fit using Nilearn's `FirstLevelModel` applied to the subject-specific fMRI time series data. The design matrix included task regressors defined by the `HCP` and `ALT` models, as well as nuisance regressors: cosine basis functions from fMRIPrep corresponding to a 128s highpass filter, and 12 motion-related parameters (three translations, three rotations, and their temporal derivatives). Time series data were pre-whitened using an AR(1) model and spatially smoothed with a 5 mm FWHM Gaussian kernel. For each run and contrast of interest (see [contrast json](./input_taskmodel.json)), Nilearn's `compute_contrast` function was used to derive the contrast estimate (effect size), its associated variance (effect variance) and z-scored statistical maps. Additionally, r-squared and residual variance maps were computed and saved for each run. The residual maps were used to extract correlation matrices from the time series data (described below).

After both runs were processed, fixed effects were computed at the subject level using Nilearn's `compute_fixed_effects` function. This was performed *only* when 1) there were two runs of data and 2) both runs had sufficient brain coverage (as determined by the mask overlap threshold). Fixed effects were computed without enabling the precision_weighted option, resulting in an unweighted average of the run-level contrast estimates.

Parcel-specific timeseries data were extracted from the residual timeseries for both models. First, the residual 4D volumes were saved for each of the two runs across all tasks for the HCP and ALT models. To restrict analyses to voxels with 1) sufficient signal and 2) anatomical plausibility, a subject-specific brain mask was computed by combining functional and anatomical criteria. First, a voxel-wise variance map was generated from the preprocessed BOLD data and binarized to include only non-zero voxels. This reflects regions with temporal variability, as variance for zero values and non-signal voxels would be zero. This was intersected with a binarized probabilistic gray matter segmentation image from the subject's anatomical data (thresholded at >1%). The resulting mask—representing the intersection of non-zero functional variance and gray matter probability—was used to constrain subsequent time series extraction and GLM estimation to relevant brain regions using `NiftiLabelsMasker` for the Schaefer 1000 deterministic atlas and `NiftiMapsMasker` for the Dimuo 1024 probabilistic atlas.

# Task Models

## Overview

Two separate models were fit to the subject-level timeseries data: `HCP` and `Alternative`. HCP models are the block-level models described in [Barch et al. 2013](https://www.sciencedirect.com/science/article/pii/S1053811913005272) for each of the seven tasks. In some cases, the HCP and Alternative models are comparable except for minor differences (e.g., in the motor task), while in others, such as the Gambling and Language tasks, they vary more meaningfully.

The variability between the models stems from two primary factors:
1. The Alternative models include response time regressors when they are sensible to include
2. The Alternative models represent stimuli and blocks differently to ensure we're modeling the construct of interest occurring at the times of the individual trials/stimuli and capturing the variability of trials (larger N) rather than blocks (lower N)

The figures below include:
1. The Design Matrix with all modeled regressors 
2. The estimated variance inflation factor (VIF) for the regressors of interest
3. The contrasts of interest, in a single subject

## Motor Task

### HCP Model
![Model for Motor](./imgs/sub-example_task-motor_mod-hcp_stat-designvifs.png)

### Alternative Model
![Model for Motor](./imgs/sub-example_task-motor_mod-alt_stat-designvifs.png)

## Gambling Task

### HCP Model
![Model for Gambling](./imgs/sub-example_task-gambling_mod-hcp_stat-designvifs.png)

### Alternative Model
![Model for Gambling](./imgs/sub-example_task-gambling_mod-alt_stat-designvifs.png)

## Emotion Task

### HCP Model
![Model for Emotion](./imgs/sub-example_task-emotion_mod-hcp_stat-designvifs.png)

### Alternative Model
![Model for Emotion](./imgs/sub-example_task-emotion_mod-alt_stat-designvifs.png)

## Social Task

### HCP Model
![Model for Social](./imgs/sub-example_task-social_mod-hcp_stat-designvifs.png)

### Alternative Model
![Model for Social](./imgs/sub-example_task-social_mod-alt_stat-designvifs.png)

## Working Memory (WM) Task

### HCP Model
![Model for WM](./imgs/sub-example_task-WM_mod-hcp_stat-designvifs.png)

### Alternative Model
![Model for WM](./imgs/sub-example_task-WM_mod-alt_stat-designvifs.png)

## Relational Task

### HCP Model
![Model for Relational](./imgs/sub-example_task-relational_mod-hcp_stat-designvifs.png)

### Alternative Model
![Model for Relational](./imgs/sub-example_task-relational_mod-alt_stat-designvifs.png)

## Language Task

### HCP Model
![Model for Language](./imgs/sub-example_task-language_mod-hcp_stat-designvifs.png)

### Alternative Model
![Model for Language](./imgs/sub-example_task-language_mod-alt_stat-designvifs.png)

# fMRI Processing Status Report

## Subject Completion Status

This report summarizes the Ns for First Level, Fixed Effect, and residual variance computed Timeseries for each of the two models.

### HCP Model

![Unique subjects and models computed](./imgs/modelsran_counts-uniqsubject_model-hcp.png)

### Alternative Model

The Alternative model fits a more complex model. In some instances, a subject that is processed using the HCP model may encounter issues in the Alternative model fitting procedure. This generally affects fewer than 5 subjects for a given task.

The First Level Status shows higher N than Fixed Effect Status. This occurs because subjects with (a) fewer than 2 runs and/or (b) poor brain coverage with an MNI template are excluded from model computation. The same criteria apply for the Timeseries Extraction.

![Unique subjects and models computed](./imgs/modelsran_counts-uniqsubject_model-alt.png)

## Data on S3 Bucket Status

This section details the number of unique subject files synchronized to the HCP AWS S3 bucket.

### HCP Model

The figure below summarizes the unique subject counts on S3 for subject folders for each model type:

![Data on S3](./imgs/s3output_counts-uniqsubject_model-hcp.png)

The following figure shows the unique file counts per subject for each task and run on S3:

![Data on S3](./imgs/s3filecounts_counts-uniqsubject_model-hcp.png)

### Alternative Model

The figure below summarizes the unique subject counts on S3 for subject folders for each model type:

![Data on S3](./imgs/s3output_counts-uniqsubject_model-alt.png)

The following figure shows the unique file counts per subject for each task and run on S3:

![Data on S3](./imgs/s3filecounts_counts-uniqsubject_model-alt.png)