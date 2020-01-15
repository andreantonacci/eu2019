import pandas as pd
import numpy as np
import time

# 5
# This code obtains all the connections between users in the data set (edges) and counts them.


def getEdges(filtered_parsed_tweets_filepath, edges_filepath):
    start_time = time.time()

    def createOrIncrement(source, target):
        # Avoid null objects
        if target == 'NA':
            return
        # Get the matching row
        match = edges_df[(source == edges_df['Source']) & (target == edges_df['Target'])]
        if match.empty:
            # Create a list for the new edge data
            match_edge_data = [source, target, 1]
            # Append a new row to edges_df with the new edge_data list
            edges_df.loc[len(edges_df)] = match_edge_data
        else:
            # Select the right cell to increment
            edges_df['Weight'] = np.where(((edges_df['Source'] == source) & (edges_df['Target'] == target)), edges_df['Weight'] + 1, edges_df['Weight'])

    # Set viz options for pandas
    # pd.set_option('display.float_format', lambda x: '%.0f' % x)  # Not needed if dtype='str'
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', -1)
    pd.set_option('display.width', 2000)
    # Load the original data frame
    df = pd.read_csv(filtered_parsed_tweets_filepath, sep='\t', dtype='str', keep_default_na=False)
    # Deal with missing values
    df = df.replace('NA', None)
    print("Step 5 started.")
    print("Files loaded. Tot number of lines:", len(df))
    # print(df.iloc[:, [2, 3, 5, 6, 8, 9, 11, 12, 13, 14]])  # For debugging

    # Define empty edges_df for the output
    edges_df = pd.DataFrame(columns=['Source', 'Target', 'Weight'])

    # Loop through all the rows in df and run the function to match rows and increment the weight (# of interactions)
    for index, row in df.iterrows():
        createOrIncrement(row['userId'], row['retweetUserId'])
        createOrIncrement(row['userId'], row['quotedUserId'])
        createOrIncrement(row['userId'], row['replyToUserId'])
        # Split userMentionsId and loop through them
        for mention_id in row['userMentionsId'].split(';'):
            createOrIncrement(row['userId'], mention_id)

    # print(edges_df)  # For debugging
    edges_df.to_csv(edges_filepath, sep='\t', encoding='utf-8', index=False)
    print("Step 5 done. Tot number of edges:", len(edges_df))
    print("It took:", time.time() - start_time)
