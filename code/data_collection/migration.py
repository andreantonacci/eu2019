import pymongo
from pymongo import MongoClient

try:
    conn = MongoClient('mongodb+srv://primaryusr:XXXXXXXXXXXX@eu-twitter-2019-mma2l.gcp.mongodb.net/test?retryWrites=true')
    print("Connected successfully")
except:
    print("Could not connect to MongoDB")

# Define db and collection to be used
db = conn.EU
elections = db.elections

con = db.elections.find()
print("Finding is done")

for x in con:

    try:
        result = db.eu2019.insert_one(x)  # Insert each JSON obj (line) into MongoDB
        result.inserted_id
    except pymongo.errors.DuplicateKeyError:
        continue

print("All done")
