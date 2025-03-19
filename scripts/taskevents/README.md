# Converting HCP E-Prime Task Timings to BIDS

The scripts here help download and convert the openly-available HCP E-Prime data to BIDS-specified events.tsv files.

## Setting up AWS

Before being able to download the eprime data, you will need to setup your AWS Client.

```bash
pip install awscli
```

After installing the AWS Client, run the below to configure your HCP credentials. (Note: Profile specification is recommended if you have different credentials).

The configuration step will ask for:

1. An Access Key for HCP
2. A Secret Key for HCP

To obtain these, login to your [HCP account](https://db.humanconnectome.org/app/template/Login.vm). Once logged in, within the *WU-Minn HCP Data - 1200 Subjects* section, look for **Amazon S3 Access**. Here, you can create and copy your (1) Access Key ID and (2) Secret Access key. Your ID will always be available but the secret key will not, so store it securely. You can always recreate it if needed.

```bash
aws configure --profile hcp
```

Once configured, verify your profile in your credentials and configuration files:

```bash
# configuration
nano ~/.aws/config
```

```bash
# credentials
nano ~/.aws/credentials
```

The `~/.aws/config` file may look like the following. Per Ross Blair, adding `s3` part optimizes S3 transfer performance:

```
[profile hcp]
s3 =
  max_concurrent_requests = 20
  max_queue_size = 30000
  max_bandwidth = 100MB/s
region = us-west-2
output = json
```

The `~/.aws/credentials` file will look like this (note, these are fake keys):
```
[hcp]
aws_access_key_id = RKIRA324234ASHDF
aws_secret_access_key = 8E8RXcAxfdadfaA9084taskrEHRm
```

## Downloading the HCP E-prime Data

To download the HCP-1200 E-Prime data, use the `download_eprimehcp.py` script. Many input values have defaults (e.g., bucket (hcp-openaccess) and subdirectory (HCP_1200)). Requirements are the AWS profile (default: hcp), output folder (default: ./hcp-eprime), and number of workers (default: 6).

```bash
uv run python download_eprimehcp.py --profile hcp --output ./hcp-eprime --workers 6
```

This script will:
- Download E-Prime data files from the HCP S3 bucket
- Search for TAB.txt files containing "eprime" in the file path for each subject
- Use parallel downloading for efficient processing across all subjects (1000+), tasks (7) and runs (2)
- Maintain the original directory structure when saving files locally

## Converting HCP E-Prime (.txt) to Events (.csv)

This script processes HCP E-Prime data files and converts them into BIDS-compatible event files. It handles multiple task types and organizes the output by subject, session and task.

### What the Script Does

The script performs the following operations:

1. Reads E-Prime tab-delimited files containing raw task data
2. Processes data based on task type using task-specific preprocessing functions
3. Transforms wide-format E-Prime data into long-format BIDS-compatible event files
4. Calculates onset times, durations, and other trial-specific information
5. Organizes output in a BIDS-compliant directory structure
6. Handles both Left-to-Right (LR) and Right-to-Left (RL) acquisition directions

For each task, the preprocessing functions:
- Label trial blocks based on procedure markers
- Calculate precise onset times and durations based on E-Prime timing information
- Extract trial types, stimulus information and participant responses
- Convert timing information from milliseconds to seconds (response times remain in milliseconds)
- Format data according to BIDS specifications

### Running the Script

To run the script, use the following command:

```bash
uv run python preprocess_hcp_eprime.py --input /home/user/data/hcp_eprime/HCP_1200 --output /home/user/data/hcp_events
```

- `--input` (required): Path to the folder containing HCP E-Prime files
- `--output` (required): Path where processed event files will be saved

### Output Structure

The script generates files with the following naming convention:
```
<output_dir>/sub-<subject_id>/ses-3T/func/sub-<subject_id>_ses-3T_task-<task_name>_dir-<LR/RL>_<run_num>_events.tsv
```

For example:
```
/home/user/data/hcp_events/sub-100307/ses-3T/func/sub-100307_ses-3T_task-wm_dir-LR_run2_events.tsv
```

### Supported Tasks

The script processes data for these HCP tasks by default:
- EMOTION
- MOTOR
- RELATIONAL
- SOCIAL
- WM (Working Memory)
- GAMBLING
- LANGUAGE

The names are UPPERCASE in the HCP E-PRIME input naming convention. The task names are converted to lowercase in the final file names.

### Reproducible Task-Schematic SVG Files

Task descriptions and trial structures were summarized to create reproducible task schematic functions. To run for the options:
- emotion
- motor
- relational
- social
- wm
- gamble
- language

use the following code:
```bash
uv --project <uv_project_directory> run python make_schematics.py --task_name <task_name>
```

## Context within E-Prime Files

The E-Prime data contains values that help us understand the structure of experimental trials, including:
- Order and sequence of different trial types
- Trial- and Block-level information
- Onset times
- Durations
- Response times

For initial blocks, timing information from E-Prime is included in parentheses to help validate the sequence of events.

These are expanded on within each task folder.