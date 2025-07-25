# HCP Data Sync SLURM Job Script

## Purpose

This SLURM batch script automates the parallel downloading (via `rclone`) of various HCP-Youth derivative datasets from a remote S3 bucket to local storage onto a separate cluster.

It supports multiple processing types:  
- `mriqc` — MRI quality control data  
- `fmriprep` — fMRI preprocessing results  
- `xcpd` — XCP-D processing outputs  
- `taskbold` — Task-level GLM outputs (alternative and HCP models)

## Usage

Submit the job array with the processing type as the first argument. For example:

```bash
sbatch hcp_rclone.sh fmriprep
```

The script reads the subject or model IDs from `${proc_type}_sub_list.txt` in the current directory, then uses the SLURM array task ID to select which subject/model to download in parallel.

## SLURM Options

- `--job-name=hcp_rlone` — job name  
- `--array=0-1000%30` — array over subjects/models with a max of 30 concurrent tasks  
- `--time=12:00:00` — max runtime (adjusted by task type)  
- `--cpus-per-task=12` — CPUs allocated per task  
- `--mem-per-cpu=2GB` — memory per CPU  
- `-p NAME` — partition used  

## Sync Options

### Option One: s3cmd + rsync

On a machine that has access to the S3 bucket via `s3cmd`, you can first pull the data locally and then `rsync` it to the target server:

```bash
s3cmd sync --recursive s3://hcp-youth/derivatives/fmriprep_v24_0_1/ses-3T/ ./local_path/
rsync -av ./local_path/ user@remote_server:/path/to/target/
```

### Option Two: rclone with s3cmd credentials

If the server where you'll be running `rclone` doesn't have native S3 access, you can export your `s3cmd` credentials and use them to configure `rclone`.

#### Step 1: Dump S3 credentials

On a machine with `s3cmd` access to s3 bucket:

```bash
s3cmd --dump-config | grep -E "access_key|secret_key|host_base"
```

#### Step 2: Create `rclone` configuration (where data is going)

You can either run:

```bash
rclone config
```

Or manually create/edit your config on the separate cluster where you plan to pull data to.

```bash
# Open rclone config file
nano /home/users/${USER}/.config/rclone/rclone.conf
```

Then add:

```
[ex-s3]
type = s3
provider = Other
access_key_id = KEY_FROM_S3CMD
secret_access_key = SECRET_FROM_S3CMD
endpoint = HOSTBASE_FROM_S3CMD
```

#### Step 3: Verify setup

Check if you can list buckets:

```bash
rclone lsd ex-s3:
```

#### Step 4: Sync or copy data

```bash
rclone sync ex-s3:hcp-youth/derivatives/mriqc_v23_1_0/ses-3T/ ./ \
    --progress \      # Show progress
    --transfers 4 \   # Download 4 files at once
    --checkers 8 \    # Use 8 threads to verify file list
    --checksum        # Ensure file integrity
```

## Notes

- Make sure the subject/model list file exists in the current directory before submitting (e.g., `fmriprep_sub_list.txt`)  
- Adjust CPU, memory and time limits depending on processing type  

