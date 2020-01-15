import json
import io
import time

# 1
# This code obtains a list of all unique User IDS that are part of a conversation and writes on conv_id file.


def getConversationId(master_data_filepath, conv_id_filepath):
    start_time = time.time()
    # Define empty array of all error lines that are skipped
    errors = []
    # Define empty data array of to-be-exported tweets
    conv_id = []
    with io.open(master_data_filepath, "r", encoding="UTF-8-sig") as master:
        for count, line in enumerate(master):  # For each line get content and index
            # if count <= 100000:  # For debugging
            if 'id_str' not in line:  # Skip error lines (e.g., not a tweet)
                errors.append(str(line))
                continue
            tweet = json.loads(line)  # Load the line
            # If it is a retweet, a quote or a reply
            if tweet.get('retweeted_status', {}).get('id_str') is not None or tweet.get('quoted_status', {}).get('id_str') is not None or tweet.get('in_reply_to_status_id_str') is not None:
                # Append the current tweet id
                conv_id.append(tweet.get('id_str'))
                # Try to append the tweet ids from sub-fields
                try:
                    conv_id.append(tweet.get('retweeted_status').get('id_str'))
                    if tweet.get('retweeted_status').get('in_reply_to_status_id_str') is not None:
                        conv_id.append(tweet.get('retweeted_status').get('in_reply_to_status_id_str'))
                except:
                    pass
                try:
                    conv_id.append(tweet.get('quoted_status').get('id_str'))
                    if tweet.get('quoted_status').get('in_reply_to_status_id_str') is not None:
                        conv_id.append(tweet.get('quoted_status').get('in_reply_to_status_id_str'))
                except:
                    pass
                if tweet.get('in_reply_to_status_id_str') is not None:
                    conv_id.append(tweet.get('in_reply_to_status_id_str'))
                # print('Added to data: line {0}'.format(count))  # For debugging

    # Construct a set out of the filtered list to remove potential duplicates
    conv_id_set = set(conv_id)

    # Write filtered_set on a txt
    with io.open(conv_id_filepath, "w", encoding="UTF-8-sig") as output:
        for tweet in conv_id_set:  # Loop through objects to add new lines between them
            output.write("%s\n" % tweet)  # Add tweet and a new line for the next object

    print("Error tweets: ", errors)
    print("Step 1 done. It took:", time.time() - start_time)

    # For debugging: open up the filtered txt and load into a list
    # conv_tweets = [line.rstrip() for line in open(filtered_output_filepath).readlines()]
    # print("conv_tweets", conv_tweets)
