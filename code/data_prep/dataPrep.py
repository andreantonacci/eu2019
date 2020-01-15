import code.data_prep.getConversationId
import code.data_prep.filterConversation
import code.data_prep.parse
import code.data_prep.getNodes
import code.data_prep.getEdges
import time
from pathlib import Path
import os


def dataPrep():
    # Identify current paths
    start_time = time.time()
    current_path = Path(__file__).resolve().parent
    assets_path = current_path.parent.parent.joinpath("assets")
    raw_data_path = assets_path.joinpath("raw_data")
    processed_data_path = assets_path.joinpath("processed_data")
    derived_data_path = assets_path.joinpath("derived")

    # Define fixed paths used in the pipeline
    master_data_filepath = raw_data_path.joinpath("master_data.json")
    conv_id_filepath = processed_data_path.joinpath("conv_id.txt")

    # Call next functions
    print("Pipeline started.")
    code.data_prep.getConversationId.getConversationId(master_data_filepath, conv_id_filepath)
    print("Conv_id file written. Elapsed minutes:", (time.time() - start_time)/60)
    # Loop through all topics files and repeat pipeline for each of them
    for file in raw_data_path.glob('tbc_topic*'):
        # Define filepaths to be used in the pipeline
        topic_filepath = raw_data_path.joinpath(file)
        current_topic = str(file.name[10:-4])
        filtered_tweets_filepath = processed_data_path.joinpath("filtered_" + current_topic + ".json")
        filtered_parsed_tweets_filepath = processed_data_path.joinpath("filtered_parsed_" + current_topic + ".csv")
        nodes_filepath = derived_data_path.joinpath("nodes_" + current_topic + ".csv")
        edges_filepath = derived_data_path.joinpath("edges_" + current_topic + ".csv")
        code.data_prep.filterConversation.filterConversation(master_data_filepath, conv_id_filepath, topic_filepath, filtered_tweets_filepath)
        print("Filtered JSON file written for topic:", file)
        print("Elapsed minutes:", (time.time() - start_time)/60)
        code.data_prep.parse.parse(filtered_tweets_filepath, filtered_parsed_tweets_filepath)
        print("Parsed CSV file written for topic:", file)
        print("Elapsed minutes:", (time.time() - start_time)/60)
        code.data_prep.getNodes.getNodes(filtered_parsed_tweets_filepath, nodes_filepath)
        print("Nodes file written for topic:", file)
        print("Elapsed minutes:", (time.time() - start_time)/60)
        code.data_prep.getEdges.getEdges(filtered_parsed_tweets_filepath, edges_filepath)
        print("Edges file written for topic:", file)
        print("All done for this topic. Elapsed minutes:", (time.time() - start_time)/60)
