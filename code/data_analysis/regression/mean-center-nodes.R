library(tidyverse)
library(modelr)
library(broom)
library(bit64)
library(data.table)
library(stargazer)
library(censReg)
library(car)

# Utilities
# rm(singlelm_df) # To remove unused object from the environment
# rm(list = ls(all.names = TRUE)) # Remove all objects including hidden objects
# gc() # Clear memory
# str(nodes) # To determine the col_types 
nodes <- fread("../../../assets/derived/brexit_metrics.csv")
scaled <- scale(nodes[,3:16], center=TRUE, scale=FALSE)
nodes_ids <- nodes[,1:2]
nodes_ids$ordering <- 1:nrow(nodes)
scaled <- as.data.frame(scaled)
scaled$ordering <- 1:nrow(scaled)
scaled_nodes <- merge(nodes_ids, scaled, by="ordering", all=TRUE)
scaled_nodes$ordering <- NULL
nodes <- scaled_nodes
rm(nodes_ids, scaled, scaled_nodes)