# RETRIEVE PARTIES
import pymongo
from pymongo import MongoClient
import csv
import json
import logging
import pysftp
import io

logging.basicConfig(level=logging.INFO, filename='eu2019_exporting_time.log', filemode='a', format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

try:
    conn = MongoClient('mongodb+srv://primaryusr:XXXXXXXXXXXX@eu-twitter-2019-mma2l.gcp.mongodb.net/test?retryWrites=true')
    logging.info("Connected successfully")
except pymongo.errors.ConnectionFailure as e:
    logging.critical("Could not connect to MongoDB. Terminating.", exc_info=True)
    exit()

# Define db and collection to be used
db = conn.EU
elections = db.elections

# Define filename to be exported
filename = "exported_tweets_time.json"

# Declare empty array
output = []

# Open file to read what keywords should be scraped
with io.open('topics_to_scrape.csv', 'r', encoding='UTF-8-sig') as csvfile:
    reader = csv.reader(csvfile)
    uniqueTopics = list(reader)
    csvfile.close()
    logging.info("Found keywords to track...")

# Loop through languages and keywords in Mongo to count them
for row in uniqueTopics:
    lang = row[0]
    print(lang)
    row.pop(0)
    print(row)
    for topic in row:
        n = db.elections.count_documents({'$and':[{'lang': lang},{'$text':{'$search': '\"'+topic+'\"'}}]})
        output.append({"lang": lang, "topic": topic, "value": n})    # append new object to output array

    logging.info("Queries for country %s were successful.", lang)

# Import and write output json file
with io.open(filename, "w", encoding="UTF-8-sig") as jsonfile:
 json.dump(output, jsonfile, ensure_ascii=False)
 logging.info("File written.")

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
    localFilePath = r"exported_tweets_time.json"

    # Define the remote path where the file will be uploaded
    remoteFilePath = '/home/query/files/' + filename

    sftp.put(localpath=localFilePath, remotepath=remoteFilePath, confirm=False)

logging.info(output)
logging.info("File pushed via SFTP. All done.")
