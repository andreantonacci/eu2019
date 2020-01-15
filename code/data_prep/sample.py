import json
import io

# Use this script to create a "random" sample file from the master ones.
# Tweak count module to set how many lines will be skipped.

# Define file paths and names
read_filepath = "PATH/TO/RAW/FILE"
write_filepath = "PATH/TO/SAMPLED/FILE"

# Define empty array
data = []
with io.open(read_filepath, "r", encoding="UTF-8-sig") as master:
    for count, line in enumerate(master):  # For each line get content and index
        if count % 20 == 0:
            data.append(json.loads(line))
            print('We are currently at line {0}'.format(count))

with io.open(write_filepath, "a", encoding="UTF-8-sig") as json_output:
    for tweet in data:  # Loop through objects to add new lines between them
        json.dump(tweet, json_output, ensure_ascii=False)
        json_output.write("\n")  # Add new line for the next object
    print("File written.")
