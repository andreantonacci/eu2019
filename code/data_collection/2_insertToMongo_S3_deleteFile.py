# LOOP through all not empty json objs
import pymongo
from pymongo import MongoClient
import json
import time
import os
import boto3
import math
import logging

logging.basicConfig(level=logging.INFO, filename='eu2019_uploading_errors.log', filemode='a', format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

# Function to insert in MongoDB
def parseFile(filepath):

    f = open(filepath, "r", encoding="UTF-8")
    content = f.readlines()
    logging.info("%s JSON file opened. Trying to upload to MongoDB...", filepath)

    counter = 0

    for c in content:
        if ('{' not in c): continue # Continue TO the next line if it does not contain a { bracket (which all JSON
                                    # objects should have! / Alternatively, you can use the len(line)

        myobject = json.loads(c)

        try:
            result = db.eu2019v3.insert_one(myobject)  # Insert each JSON obj (line) into MongoDB
            result.inserted_id
        except pymongo.errors.DuplicateKeyError as e:
            logging.error("Duplicate Row no. %d of file %s", counter, filepath, exc_info=False)
            continue
        except pymongo.errors.WriteError as e2:
            logging.critical("Could not insert line %d of file %s", counter, filepath, exc_info=True)

        counter = counter + 1       # Increase the counter by 1 at every iteration

    f.close()
    logging.info("Correctly inserted to MongoDB.")

# Function to backup on S3
def uploadToS3(filepath, filename):

    logging.info("Trying to upload to S3 file... %s", filename)

    # Uploads the given file via a managed uploader, which will split up large files automatically and upload in parallel
    try:
        s3.upload_file(filepath, bucket_name, filename)
        logging.info("Upload to S3 OK.")
        return True
    except boto3.exceptions.S3UploadFailedError as e:
        logging.critical("Upload to S3 ERROR.", exc_info=True)
        return False

# Function to delete managed files
def deleteFile(filepath):
    try:
        os.remove(filepath)
        logging.info("File removed. %s", filepath)
    except OSError as e:
        logging.critical("Can't delete file. %s", filepath, exc_info=True)

# Function to move files to /Errors when an error is raised
def moveFile(filepath, filename):
    try:
        os.rename(filepath, errorDirectory + "/" + filename)
        logging.error("File moved to /Errors: %s", filepath)
    except OSError as e:
        logging.critical("Can't move file: %s", filepath, exc_info=True)

# Connect to MongoDB
try:
    conn = MongoClient('mongodb+srv://primaryusr:XXXXXXXXXXXX@eu-twitter-2019-mma2l.gcp.mongodb.net/test?retryWrites=true')
    logging.info("Connected successfully")
except pymongo.errors.ConnectionFailure as e:
    logging.critical("Could not connect to MongoDB. Terminating.", exc_info=True)
    exit()

# Define db and collection to be used
db = conn.EU
eu2019v3 = db.eu2019v3

# Create an S3 client and configure from shell
s3 = boto3.client('s3')
bucket_name = 'INSERT-YOURS'

# Dir to JSON files
directory = "./Raw"
errorDirectory = "./Errors"

# Loop through files in directory
while True:
    for file in os.scandir(directory):
        logging.info("Loading file... %s", file)
        fileTimeStamp = file.stat().st_mtime               # Last modified timestamp of the file
        currentTimeStamp = time.time()                     # Time right now
        diff = (currentTimeStamp - fileTimeStamp)          # Difference in secs between the two
        logging.info("Time diff: %s", diff)

        if file.name.endswith(".json") and diff > 5 * 60:  # Only work on JSON files older than 5 mins
            parseFile(file.path)
            uploadResult = uploadToS3(file.path, file.name)
            # Only delete files if uploadToS3 is successful, otherwise move to /Errors
            if uploadResult is True:
                deleteFile(file.path)
                logging.info("All done.")
            else:
                moveFile(file.path, file.name)
    # Sleep for 5 mins if directory is empty and try again
    logging.info("Sleeping for 5 mins...")
    time.sleep(5*60)
    logging.info("Waking up...")
