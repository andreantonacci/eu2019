from pathlib import Path
import boto3
import time

start_time = time.time()
# Configure AWS S3 and files to be downloaded (make sure AWS CLI is configured too)
s3 = boto3.client("s3")
bucket_name = "eu2019"
downloads = ["raw/eu2019.json", "raw/eu2019v2.json", "raw/eu2019v3.json"]


# Launch pipeline
def takeOff():
    import code.data_prep.dataPrep
    code.data_prep.dataPrep.dataPrep()


# Download data from S3
def downloadFromS3(object_path, local_path):
    # downloads the file via a managed uploader, which will split up large files automatically and download in parallel
    try:
        s3.download_file(bucket_name, object_path, local_path)
        print("Download from S3 OK:", object_path)
        return True
    except boto3.exceptions.S3UploadFailedError as e:
        print("Download from S3 ERROR:", e)
        return False


# Process starts below
print("Initializing directories...")
current_path = Path(__file__).resolve().parent
# Mkdir code directory
code_path = current_path.joinpath("code")
Path(code_path).mkdir(parents=True, exist_ok=True)
# Mkdir code sub-directories
data_prep_path = code_path.joinpath("data_prep")
data_analysis_path = code_path.joinpath("data_analysis")
data_collection_path = code_path.joinpath("data_collection")
Path(data_prep_path).mkdir(parents=True, exist_ok=True)
Path(data_analysis_path).mkdir(parents=True, exist_ok=True)
Path(data_collection_path).mkdir(parents=True, exist_ok=True)
# Move Python files to sub-directories
for f in current_path.glob('*.py'):
    if f.stem not in ["initialize", "__init__"]:
        f.rename(data_prep_path.joinpath(f.name))
# Create __init__ files in the right directories
Path(current_path.joinpath("__init__.py")).touch(exist_ok=True)
Path(code_path.joinpath("__init__.py")).touch(exist_ok=True)
# Mkdir assets directory
assets_path = current_path.joinpath("assets")
Path(assets_path).mkdir(parents=True, exist_ok=True)
# Mkdir assets sub-directories
derived_path = assets_path.joinpath("derived")
processed_data_path = assets_path.joinpath("processed_data")
raw_data_path = assets_path.joinpath("raw_data")
temp_path = assets_path.joinpath("temp")
Path(derived_path).mkdir(parents=True, exist_ok=True)
Path(processed_data_path).mkdir(parents=True, exist_ok=True)
Path(raw_data_path).mkdir(parents=True, exist_ok=True)
Path(temp_path).mkdir(parents=True, exist_ok=True)

# Move raw data to subdirectory
for f in current_path.glob("tbc_topic*"):
    f.rename(raw_data_path.joinpath(f.name))
for f in current_path.glob("*sample.json"):  # For debugging
    f.rename(raw_data_path.joinpath(f.name))

# Retrieve raw data from AWS S3
print("Directories initialized. Retrieving files from S3...")
for download in downloads:
    downloadFromS3(download, str(raw_data_path.joinpath(download[4:])))  # local path is raw path + download w/o "raw/"
print("Files downloaded. Merging files together... Elapsed minutes:", (time.time() - start_time)/60)

# Merge raw data files into one master_data JSON file
with open(processed_data_path.joinpath("master_data.json"), "w") as master_data_file:
    for f in raw_data_path.glob("eu2019*"):
        with open(f) as infile:
            master_data_file.write(infile.read())

print("Files merged. Elapsed minutes:", (time.time() - start_time)/60)
print("Process starting up...")
# Call next function
takeOff()
print("ALL JOBS DONE! :) TOT RUNTIME (mins):", (time.time() - start_time)/60)
