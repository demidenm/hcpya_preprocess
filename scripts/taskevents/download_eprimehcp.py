import os
import subprocess
import concurrent.futures
import argparse

def get_subject_ids(bucket_name, prefix, profile):
    """Get list of subject IDs from the S3 bucket"""
    command = f"aws s3 ls s3://{bucket_name}/{prefix}/ --profile {profile}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    subject_ids = []
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            # Remove trailing slash from directory names
            subject_id = parts[1].rstrip('/')
            subject_ids.append(subject_id)
    
    return subject_ids

def get_subject_files(bucket_name, prefix, subject_id, profile):
    """Get list of files for a specific subject that match the criteria"""
    command = f"aws s3 ls --recursive s3://{bucket_name}/{prefix}/{subject_id}/unprocessed/3T/ --profile {profile}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    files = []
    for line in result.stdout.splitlines():
        if "eprime" in line.lower() and "TAB.txt" in line:
            parts = line.split()
            if len(parts) >= 4:
                file_path = parts[3]
                files.append(file_path)
    
    return files

def download_file(bucket_name, file_path, output_folder, profile):
    """Download a single file from S3 to the specified output folder"""
    # Construct the local file path
    local_file_path = os.path.join(output_folder, file_path)
    
    # Create directory structure if it doesn't exist
    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
    
    # Download the file using aws cli
    command = f"aws s3 cp s3://{bucket_name}/{file_path} {local_file_path} --profile {profile}"
    subprocess.run(command, shell=True, check=True)
    
    return local_file_path


# Parse command line arguments
parser = argparse.ArgumentParser(description='Download files from S3 bucket')
parser.add_argument('--profile', type=str, default="hcp", help='AWS profile to use')
parser.add_argument('--output', type=str, default="./hcp-eprime", help='Output folder for downloaded files')
parser.add_argument('--workers', type=int, default=6, help='Number of parallel downloads')

args = parser.parse_args()

# Configuration from command line args
bucket_name = "hcp-openaccess"
prefix = 'HCP_1200'
profile = args.profile
output_folder = args.output
max_workers = args.workers

# Create output directory if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Get subject IDs
print(f"Getting subject IDs from bucket: {bucket_name}, prefix: {prefix}...")
subject_ids = get_subject_ids(bucket_name, prefix, profile)

# Process each subject
for subject_id in subject_ids:
    print(f"Processing subject: {subject_id}")
    
    # Get list of files for this subject
    files = get_subject_files(bucket_name, prefix, subject_id, profile)
    
    if not files:
        print(f"No matching files found for subject {subject_id}")
        continue
        
    # Download files in parallel using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create a list of futures
        future_to_file = {
            executor.submit(download_file, bucket_name, file_path, output_folder, profile): file_path 
            for file_path in files
        }
        
        # Process as they complete
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                downloaded_path = future.result()
                print(f"Downloaded: {downloaded_path}")
            except Exception as e:
                print(f"Error downloading {file_path}: {e}")