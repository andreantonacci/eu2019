import tweepy
from tweepy.auth import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
import time
import math
import logging

logging.basicConfig(level=logging.INFO, filename='eu2019_raw_collection_errors.log', filemode='a', format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

# Path to list of tracked keywords
f=open('./Hashtags/primary_tracked_keywords.csv', 'r', encoding='utf-8')

con=f.read()
keywords=[]
newlist=con.split("';'")

for has in newlist:
    keywords.append(has.replace("'","").replace('\n',''))

# This part is responsible of getting the data, and printing the data.
# It's a basic listener, writing tweets to the output file (filename).
class StdOutListener(StreamListener):
    def on_data(self, data):
        #print data

        timestr = time.strftime("%Y%m%d-%H") # first part of the timestamp
        minute = int(time.strftime("%M")) # retrieve minutes as int
        mininterval = math.ceil(minute/5) # define interval time
        minutestr = str(mininterval)
        filename = ".\Raw/primary-"+ timestr + "-" + minutestr + ".json"
        with open(filename,'a') as tf:
            tf.write(data)
        return True

    def on_error(self, status):
        logging.critical("Error on collection: %s", status)

l = StdOutListener()

# Please add your Twitter API user credentials here.

access_token = "INSERT-YOURS"
access_token_secret = "INSERT-YOURS"
consumer_key = "INSERT-YOURS"
consumer_secret = "INSERT-YOURS"

# Define a list of trackable hash tags or character strings
# that you would like to get data on.

tracking = keywords

#logging.info('Writing to... %s', filename)

while True:
    try:
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        stream = Stream(auth, l)
        stream.filter(track=tracking)
    except:
        logging.critical('Error in data collection; check internet connection and API retrieval limit. If this error persists, please restart Jupyter Notebook.')
