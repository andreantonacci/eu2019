import pandas as pd
import numpy as np
import time

# 4
# This code obtains a list of all the unique IDs (nodes) from the parsed CSV file:
# user ids, retweet user ids, replies, etc...


def getNodes(filtered_parsed_tweets_filepath, nodes_filepath):
    start_time = time.time()
    # Set viz options for pandas
    # pd.set_option('display.float_format', lambda x: '%.0f' % x)  # Not needed if dtype='str'
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', -1)
    pd.set_option('display.width', 2000)
    # Load the original data frame
    df = pd.read_csv(filtered_parsed_tweets_filepath, sep='\t', dtype='str', keep_default_na=False)
    # Deal with missing values
    df = df.replace('NA', np.nan)
    print("Step 4 started.")
    print("File loaded. Tot number of lines:", len(df))
    # print(df.iloc[:, [2, 3, 5, 6, 8, 9, 11, 12, 13, 14]])  # For debugging
    # Create new data frames for all types of tweets in the original df
    df_seeds = df[['userId', 'userScreenName']].copy()
    df_retweets = df[['retweetUserId', 'retweetUserScreenName']].copy()
    df_quotes = df[['quotedUserId', 'quotedUserScreenName']].copy()
    df_replies = df[['replyToUserId', 'replyToUserScreenName']].copy()
    df_mentions_list = df[['userMentionsId', 'userMentionsScreenName']].copy()
    # Split multiple userMentionsId and userMentionsScreenName into rows, first by creating two series
    s1 = df_mentions_list.userMentionsId.str.split(';', expand=True).stack().str.strip().reset_index(level=1, drop=True)
    s2 = df_mentions_list.userMentionsScreenName.str.split(';', expand=True).stack().str.strip().reset_index(level=1, drop=True)
    # Concat series to a new df to be used in the final df_output
    df_mentions = pd.concat([s1, s2], axis=1, keys=['userMentionsId', 'userMentionsScreenName']).reset_index(drop=True)
    # print(df_mentions)  # For debugging
    # Create list of all frames to be concatenated and rename columns to allow the merge
    frames = [df_seeds.rename(columns={'userId': 'Id', 'userScreenName': 'Label'}), df_retweets.rename(columns={'retweetUserId': 'Id', 'retweetUserScreenName': 'Label'}), df_quotes.rename(columns={'quotedUserId': 'Id', 'quotedUserScreenName': 'Label'}), df_replies.rename(columns={'replyToUserId': 'Id', 'replyToUserScreenName': 'Label'}), df_mentions.rename(columns={'userMentionsId': 'Id', 'userMentionsScreenName': 'Label'})]
    # Create new output df from the frames list
    df_output = pd.concat(frames, ignore_index=True)
    # Ignore all NaN values
    df_output = df_output[pd.notnull(df_output['Id'])].reset_index(drop=True)
    # Drop all rows with Id that is not unique
    df_output = df_output.drop_duplicates(subset='Id').reset_index(drop=True)  # Why doesn't it work with subset=Id???
    # print(df_output.iloc[:, :])  # For debugging
    # Write output file
    df_output.to_csv(nodes_filepath, sep='\t', encoding='utf-8', index=False)
    print("Step 4 done. Tot number of nodes:", len(df_output))
    print("It took:", time.time() - start_time)
