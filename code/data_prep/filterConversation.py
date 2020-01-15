import json
import io
import time

# 2
# This code filters the tweets from the original master data according to their User ID and hashtags included.
# Two conditions must be met: their User ID is in the conv_id file and at least one of their hashtag texts is contained
# in the texts (i.e., is a sub-string) of any of the tracked hashtags (contained in the topic_filepath).


def filterConversation(master_data_filepath, conv_id_filepath, topic_filepath, filtered_tweets_filepath):
    start_time = time.time()
    # Initialize counter of badly formatted lines
    error_count = 0
    # Define empty data array of to-be-exported tweets
    filtered_tweets = []
    # Define sets for the required data inputs
    conv_tweets = set()
    topics = set()

    with open(conv_id_filepath, "r", encoding="UTF-8-sig") as f:
        for line in f:
            conv_tweets.add(line.rstrip())

    with open(topic_filepath, "r", encoding="UTF-8-sig") as f:
        for line in f:
            topics.add(line.rstrip().lower())

    print("Step 2 started.")
    with open(master_data_filepath, "r", encoding="UTF-8-sig") as master:
        for idx, line in enumerate(master):  # For each line get content and index
            # if idx == 100000:  # For debugging
            #     break
            if 'id_str' not in line:  # Skip error lines (e.g., not a tweet)
                error_count += 1
                continue
            # Load the content of the line
            tweet = json.loads(line)
            tweet_id = tweet.get('id_str')
            # Look for hashtags only if present
            tbc_hashtags_outlist = []
            hashtags = tweet.get('entities').get('hashtags')
            if len(hashtags) > 0:
                for hashtag in hashtags:
                    tbc_hashtags_outlist.append(hashtag.get('text').replace('\t', ' ').replace('\n', '').lower())
            # Add only matching tweets (with any id in conv_tweets and with any hashtag in topic) to filtered_tweets
            if tweet_id in conv_tweets:
                for tbc_tweet_hashtag in tbc_hashtags_outlist:
                    for topic in topics:
                        if topic in tbc_tweet_hashtag:
                            filtered_tweets.append(tweet)

    print("Number of badly formatted lines: ", error_count)
    print("Writing output file...")

    # Write output file
    with io.open(filtered_tweets_filepath, "w", encoding="UTF-8-sig") as json_output:
        for tweet in filtered_tweets:  # Loop through objects to add new lines between them
            json.dump(tweet, json_output, ensure_ascii=False)
            json_output.write("\n")  # Add new line for the next object

    print("Step 2 done. It took:", time.time() - start_time)
