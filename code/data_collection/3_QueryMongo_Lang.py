# RETRIEVE LANG
import pymongo
from pymongo import MongoClient
import json
import pysftp
import logging
import os
import io
import csv

logging.basicConfig(level=logging.INFO, filename='eu2019_exporting_lang.log', filemode='a', format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

try:
    conn = MongoClient('mongodb+srv://primaryusr:XXXXXXXXXXXX@eu-twitter-2019-mma2l.gcp.mongodb.net/test?retryWrites=true')
    logging.info("Connected successfully")
except pymongo.errors.ConnectionFailure as e:
    logging.critical("Could not connect to MongoDB. Terminating.", exc_info=True)
    exit()

# Define db and collection to be used
db = conn.EU
eu2019v3 = db.eu2019v3

# Define filename to be exported
filename = "exported_tweets_lang_post.json"

# declare empty array
countries = []

with io.open('languages_list.csv', 'r', encoding='UTF-8-sig') as csvfile:
    reader = csv.reader(csvfile)
    uniqueLangs = list(reader)
    csvfile.close()
    logging.info("Found keywords to track...")

for lang in uniqueLangs:
    lang = str(lang)[2:-2]
    n = db.eu2019v3.count_documents( { "lang": lang } )  # count how many tweets are in "value" lang
    countries.append({"lang": lang, "value": n})       # append new object to country array
    logging.info("Query for %s was successful.", lang)

# Import and write json file
with io.open(filename, "w", encoding="UTF-8-sig") as file:
 json.dump(countries, file, ensure_ascii=False)

# Verify sftp server
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

# Connect via SFTP
myHostname = "electionstats.eu"
myUsername = "XXXXX"
myPassword = "XXXXX"

with pysftp.Connection(host=myHostname, username=myUsername, password=myPassword, cnopts=cnopts) as sftp:
    logging.info("SFTP connection succesfully established ... ")

    # Define the file that you want to upload from your local directorty
    # or absolute "C:\Users\sdkca\Desktop\TUTORIAL2.txt"
    localFilePath = r"exported_tweets_lang_post.json"

    # Define the remote path where the file will be uploaded
    remoteFilePath = '/home/query/files/' + filename

    sftp.put(localpath=localFilePath, remotepath=remoteFilePath, confirm=False)

logging.info("Tot languages: %s", countries)
logging.info("All done")
