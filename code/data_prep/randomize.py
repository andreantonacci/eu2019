import random
from pathlib import Path

# This code is used to obtain a random sample of lines

current_path = Path(__file__).resolve().parent
read_file = current_path.joinpath("PATH/TO/RAW/FILE")
write_file = current_path.joinpath("PATH/TO/SAMPLED/FILE")
with open(read_file,"r",encoding="utf-8-sig") as source:
    data = [ (random.random(), line) for line in source ]
data.sort()
with open(write_file,"w",encoding="utf-8-sig") as target:
    for _, line in data:
        target.write(line)
