# RETRIEVE PARTIES
import pymongo
from pymongo import MongoClient
import csv
import json
import logging
import pysftp
import io

logging.basicConfig(level=logging.INFO, filename='eu2019_exporting_parties.log', filemode='a', format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

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
filename = "exported_tweets_parties_post.json"

# Declare empty array
output = []

# Open file to read what keywords should be scraped
with io.open('parties_to_scrape.csv', 'r', encoding='UTF-8-sig') as csvfile:
    reader = csv.reader(csvfile)
    uniqueParties = list(reader)
    csvfile.close()
    logging.info("Found parties to track...")

# Loop through languages and keywords in Mongo to count them
for row in uniqueParties:
    country = row.pop(0)
    lang = row.pop(0)
    print(lang)
    print(row)
    for party in row:
        n = db.eu2019v3.count_documents({'$and':[{'lang': lang},{'$text':{'$search': '\"'+party+'\"'}}]})
        output.append({"country": country, "language": lang, "party": party, "value": n})    # append new object to output array

    logging.info("Queries for country %s were successful.", country)

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
    localFilePath = r"exported_tweets_parties_post.json"

    # Define the remote path where the file will be uploaded
    remoteFilePath = '/home/query/files/' + filename

    sftp.put(localpath=localFilePath, remotepath=remoteFilePath, confirm=False)

logging.info(output)
logging.info("File pushed via SFTP. All done.")
