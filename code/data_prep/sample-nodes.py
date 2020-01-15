import pandas as pd

# This code is used to sample nodes for a given topic (used for the topic: brexit)
# Create nodes_brexit_sampled.csv
step = 15

df_nodes = pd.read_csv('nodes_brexit.csv', sep='\t')
df_nodes_sampled = df_nodes.iloc[::step, :]

# Create edges_brexit_sampled.csv
df_edges = pd.read_csv('edges_brexit.csv', sep='\t')

mask = df_edges['Source'].isin(df_nodes_sampled['Id'])
df_edges = df_edges[mask] # only select rows where the column Source contains an Id which is in series_nodes

series_nodes_complete = df_edges['Source'].append(df_edges['Target']).drop_duplicates()
print(series_nodes_complete.shape)

df_nodes_complete = df_nodes[df_nodes['Id'].isin(series_nodes_complete)]

df_nodes_complete.to_csv('nodes_brexit_sampled.csv', sep='\t', index=False)
df_edges.to_csv('edges_brexit_sampled.csv', sep='\t', index=False)
