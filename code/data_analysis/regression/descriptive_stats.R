library(tidyverse)
library(modelr)
library(broom)
library(bit64)
library(data.table)
library(stargazer)
library(censReg)
library(car)

# Script to get summary statistics for each topic - standalone

# Utilities
# rm(singlelm_df) # To remove unused object from the environment
# rm(list = ls(all.names = TRUE)) # Remove all objects including hidden objects
# gc() # Clear memory
# str(nodes) # To determine the col_types 

# Declare path of Gephi metrics csv files
metrics_files <- list.files(path="../../../assets/derived/", pattern=".*\\_metrics.csv", recursive=TRUE)

# Define functions
getNodes <- function(topic, nodes_filepath) {
  # Load nodes data with Gephi network metrics
  nodes <- fread(nodes_filepath)
  print(nodes)
  return(nodes)
}

outputToFile <- function(topic, nodes) {
  
  # Get txt output file
  output_filename = paste(topic, "_summary_output.txt", sep="")
  table_title = paste("Summary stats for topic: ", topic, sep="")
  sink(output_filename)
  stargazer(nodes[,3:16], title=table_title, summary=TRUE, initial.zero = FALSE)
  sink()
}

#################
### Run below ###
#################

# Loop thourgh metrics files and apply getNodes function
dataframes_list <- lapply(metrics_files, function(filename) {
  topic <- gsub("_metrics.csv", "", filename, fixed = TRUE)
  nodes_filepath <- paste("../../../assets/derived/", topic, "_metrics.csv", sep="")
  df_name <- paste(topic, "_summary_stats", sep="")
  df_name <- getNodes(topic, nodes_filepath)
  df_info <- list("topic" = topic, "nodes" = df_name)
  return(df_info)
})

# Loop through dataframes and apply outputToFile function
models_output <- lapply(dataframes_list, function(one_element) {
  return(outputToFile(one_element$topic, one_element$nodes))
  print(one_element$topic)
})

# Clear all, and save
# save.image(file="forhannes.RData")
rm(list = ls(all.names = TRUE))
gc()

# Misc
tidy(multilm) # Access coefficients
confint(multilm) # Get confidence intervals
sigma(multilm) # Get sigma = RSE in summary
rsquare(multilm, data=df) # R2 as in summary


