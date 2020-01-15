import json
import time

# 3
# This code parses the filtered tweets' JSON file, keeping only relevant fields for social network analysis.


def parse(filtered_tweets_filepath, filtered_parsed_tweets_filepath):
    start_time = time.time()
    # Define empty array of all possibly skipped lines
    skipped = []
    # Open and write csv header
    csv_output = open(filtered_parsed_tweets_filepath, "w", encoding="UTF-8-sig")
    csv_output.write('timestamp' + '\t' +
                     'tweetId' + '\t' +
                     'userId' + '\t' +
                     'userScreenName' + '\t' +
                     # 'tweetText' + '\t' +
                     # 'hashtags' + '\t' +
                     # 'followersCount' + '\t' +
                     # 'device' + '\t' +
                     # 'lang' + '\t' +
                     # 'userLang' + '\t' +
                     # 'userLocation' + '\t' +
                     'retweetId' + '\t' +
                     'retweetUserId' + '\t' +
                     'retweetUserScreenName' + '\t' +
                     'quoteId' + '\t' +
                     'quotedUserId' + '\t' +
                     'quotedUserScreenName' + '\t' +
                     'replyToTweetId' + '\t' +
                     'replyToUserId' + '\t' +
                     'replyToUserScreenName' + '\t' +
                     'userMentionsId' + '\t' +
                     'userMentionsScreenName' +
                     '\n')

    with open(filtered_tweets_filepath, "r", encoding="UTF-8-sig") as master:
        for count, line in enumerate(master):  # For each line get content and index
            if 'id_str' not in line:
                skipped.append(str(line))
                continue  # continue (skip) to the next line if it does not contain an id_str
            # print('We are currently at line {0} '.format(count))
            tweet = json.loads(line)  # Load the line

            # Parsing below
            timestamp = str(tweet.get('created_at'))

            tweetId = str(tweet.get('id_str').replace('\t', ' ').replace('\n', ''))

            userId = str(tweet.get('user').get('id_str').replace('\t', ' ').replace('\n', ''))

            userScreenName = str(tweet.get('user').get('screen_name').replace('\t', ' ').replace('\n', ''))

            # tweetText = str(tweet.get('text').replace('\t', ' ').replace('\n', ''))

            # Look for hashtags only if present, NA otherwise
            # if len(tweet.get('entities').get('hashtags')) > 0:
            #     hashtags_outlist = []
            #     for hashtag in tweet.get('entities').get('hashtags'):
            #         hashtags_outlist.append(hashtag.get('text'))
            #     hashtags = '; '.join(hashtags_outlist)
            # else:
            #     hashtags = 'NA'
            #
            # followersCount = str(tweet.get('user').get('followers_count'))
            #
            # device = str(tweet.get('source').replace('\t', ' ').replace('\n', ''))
            #
            # lang = str(tweet.get('lang'))
            #
            # userLang = str(tweet.get('user').get('lang'))
            #
            # try:
            #     userLocation = str(tweet.get('user').get('location').replace('\t', ' ').replace('\n', ''))
            # except:
            #     userLocation = 'NA'
            #
            try:
                retweetId = str(tweet.get('retweeted_status').get('id_str').replace('\t', ' ').replace('\n', ''))
            except:
                retweetId = 'NA'

            try:
                retweetUserId = str(tweet.get('retweeted_status').get('user').get('id_str').replace('\t', ' ').replace('\n', ''))
            except:
                retweetUserId = 'NA'

            try:
                retweetUserScreenName = str(tweet.get('retweeted_status').get('user').get('screen_name').replace('\t', ' ').replace('\n', ''))
            except:
                retweetUserScreenName = 'NA'

            try:
                quoteId = str(tweet.get('quoted_status').get('id_str').replace('\t', ' ').replace('\n', ''))
            except:
                quoteId = 'NA'

            try:
                quotedUserId = str(tweet.get('quoted_status').get('user').get('id_str').replace('\t', ' ').replace('\n', ''))
            except:
                quotedUserId = 'NA'

            try:
                quotedUserScreenName = str(tweet.get('quoted_status').get('user').get('screen_name').replace('\t', ' ').replace('\n', ''))
            except:
                quotedUserScreenName = 'NA'

            try:
                replyToTweetId = str(tweet.get('in_reply_to_status_id_str').replace('\t', ' ').replace('\n', ''))
            except:
                replyToTweetId = 'NA'

            try:
                replyToUserId = str(tweet.get('in_reply_to_user_id_str').replace('\t', ' ').replace('\n', ''))
            except:
                replyToUserId = 'NA'

            try:
                replyToUserScreenName = str(tweet.get('in_reply_to_screen_name').replace('\t', ' ').replace('\n', ''))
            except:
                replyToUserScreenName = 'NA'

            # Look for user_mentions only if present, NA otherwise
            if len(tweet.get('entities').get('user_mentions')) > 0:
                user_mentions_id_outlist = []
                user_mentions_name_outlist = []
                for user_mention in tweet.get('entities').get('user_mentions'):
                    user_mentions_id_outlist.append(str(user_mention.get('id_str')))
                    user_mentions_name_outlist.append(str(user_mention.get('screen_name')))
                userMentionsId = ';'.join(user_mentions_id_outlist)
                userMentionsScreenName = ';'.join(user_mentions_name_outlist)
            else:
                userMentionsId = 'NA'
                userMentionsScreenName = 'NA'

            # Write a new line to the csv file
            csv_output.write(timestamp + '\t' +
                             tweetId + '\t' +
                             userId + '\t' +
                             userScreenName + '\t' +
                             # tweetText + '\t' +
                             # hashtags + '\t' +
                             # followersCount + '\t' +
                             # device + '\t' +
                             # lang + '\t' +
                             # userLang + '\t' +
                             # userLocation + '\t' +
                             retweetId + '\t' +
                             retweetUserId + '\t' +
                             retweetUserScreenName + '\t' +
                             quoteId + '\t' +
                             quotedUserId + '\t' +
                             quotedUserScreenName + '\t' +
                             replyToTweetId + '\t' +
                             replyToUserId + '\t' +
                             replyToUserScreenName + '\t' +
                             userMentionsId + '\t' +
                             userMentionsScreenName +
                             '\n')

    csv_output.close()
    print("Skipped lines: ", skipped)
    print("Step 3 done. It took:", time.time() - start_time)
