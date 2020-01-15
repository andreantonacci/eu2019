library(tidyverse)
library(modelr)
library(broom)
library(bit64)
library(data.table)
library(stargazer)
library(censReg)
library(car)
library(ggpubr)

# Main script to wrangle data and run regressions

# Utilities
# rm(singlelm_df) # To remove unused object from the environment
# rm(list = ls(all.names = TRUE)) # Remove all objects including hidden objects
# gc() # Clear memory
# str(nodes) # To determine the col_types 

# Declare path of Gephi metrics csv files
metrics_files <- list.files(path="../../../assets/derived/", pattern=".*\\_metrics.csv", recursive=TRUE)

# Define functions
dataModelling <- function(topic, nodes_filepath, edges_filepath) {
  # Load nodes data with Gephi network metrics
  nodes <- fread(nodes_filepath)
  nodes
  
  options(scipen=999) # Do not display scientific notation
  
  # Mean-center all nodes
  scaled <- scale(nodes[,3:16], center=TRUE, scale=FALSE)
  nodes_ids <- nodes[,1:2]
  nodes_ids$ordering <- 1:nrow(nodes)
  scaled <- as.data.frame(scaled)
  scaled$ordering <- 1:nrow(scaled)
  scaled_nodes <- merge(nodes_ids, scaled, by="ordering", all=TRUE)
  scaled_nodes$ordering <- NULL
  nodes <- scaled_nodes
  rm(nodes_ids, scaled, scaled_nodes)
  
  # Get all unique IDs
  unique_ids=unique(nodes$Id)
  
  # Get all possible combinations of interaction between users (IDs)
  interactions_df = rbindlist(lapply(unique_ids, function(x) {
    class(x)="integer64"
    return(data.table(Id1=rep(x, length(unique_ids)), Id2=as.integer64(unique_ids)))
  }))
  
  # Update interactions_df removing self-tweeting
  interactions_df=interactions_df[!Id1==Id2] 
  interactions_df=interactions_df[!Id1==as.integer64(0)]
  interactions_df=interactions_df[!Id2==as.integer64(0)]
  
  # Merge nodes with interactions_df, keys are the IDs
  interactions_df2 <- merge(interactions_df, nodes, by.x=c("Id1"), by.y=c("Id"), all.x=T, all.y=F)
  
  # Duplicate nodes and rename cols for the second user (target)
  nodes2=copy(nodes)
  setnames(nodes2, paste0("u2_", colnames(nodes2)))
  
  # Get final df (left join on target user (u2) with their metrics)
  df <- merge(interactions_df2, nodes2, by.x=c("Id2"), by.y=c("u2_Id"), all.x=T, all.y=F)
  
  # Load edges data
  edges <- fread(edges_filepath)
  
  # Set keys for upcoming merge
  setkey(edges, Source, Target)
  setkey(df, Id1, Id2)
  
  # Add number of comm to df
  df[edges, communication:=i.Weight]
  setcolorder(df, c("Id1","Id2", "communication"))
  df[is.na(communication), communication:=0]
  
  # Rename columns to remove spaces
  names(df)[names(df) == "weighted indegree"] <- "weighted_indegree"
  names(df)[names(df) == "weighted outdegree"] <- "weighted_outdegree"
  names(df)[names(df) == "Weighted Degree"] <- "weighted_degree"
  names(df)[names(df) == "u2_weighted indegree"] <- "u2_weighted_indegree"
  names(df)[names(df) == "u2_weighted outdegree"] <- "u2_weighted_outdegree"
  names(df)[names(df) == "u2_Weighted Degree"] <- "u2_weighted_degree"
  
  # Add new dummy interacted, which takes value 1 if comm > 0, and reset order
  df <- mutate(df, interacted = ifelse(communication > 0, 1, 0))
  setcolorder(df, c("Id1","Id2", "communication", "interacted"))
  
  # Finally remove unused df and free up memory, export to csv if necessary 
  rm(interactions_df, interactions_df2, nodes2)
  # fwrite(df, "r_export.csv", sep='\t')
  return(df)
}

dataAnalysis <- function(topic, df) {
  # First lm
  multilm <- lm(communication ~ outdegree + eigencentrality + clustering + u2_outdegree + u2_eigencentrality + u2_clustering + clustering*u2_clustering, data=df)
  # summary(multilm)
  
  # Logit with interaction dummy
  logit <- glm(interacted ~ outdegree + eigencentrality + clustering + u2_outdegree + u2_eigencentrality + u2_clustering + clustering*u2_clustering, data=df, family=binomial)
  # summary(logit)
  
  # Conditional lm (if comm > 0)
  multilm_interacted <- lm(communication ~ outdegree + eigencentrality + clustering + u2_outdegree + u2_eigencentrality + u2_clustering + clustering*u2_clustering, data=df, subset=communication>0)
  # summary(multilm_interacted)
  
  # Retrieve coef table for multilm with conf.intervals for subsequent plots
  multilm_cf <- as.data.frame(confint.default(multilm, level=0.95))
  multilm_cf$ordering <- 1:nrow(multilm_cf)
  
  multilm_coef <- tidy(multilm) # Get coefficients
  multilm_coef$ordering <- 1:nrow(multilm_coef)
  
  multilm_cf_coef <- merge(multilm_coef, multilm_cf, by="ordering", all=TRUE) # Merge coefficients with cf
  multilm_cf_coef$ordering <- NULL # Drop column used as index
  multilm_coef <- multilm_cf_coef # Rename df and columns
  names(multilm_coef)[names(multilm_coef) == "2.5 %"] <- "conf.low"
  names(multilm_coef)[names(multilm_coef) == "97.5 %"] <- "conf.high"
  rm(multilm_cf, multilm_cf_coef) # Remove unused stuff
  
  # Retrieve coef table for logit with conf.intervals for subsequent plots
  logit_cf <- as.data.frame(confint.default(logit, level=0.95))
  logit_cf$ordering <- 1:nrow(logit_cf)
  
  logit_coef <- tidy(logit) # Get coefficients
  logit_coef$ordering <- 1:nrow(logit_coef)
  
  logit_cf_coef <- merge(logit_coef, logit_cf, by="ordering", all=TRUE) # Merge coefficients with cf
  logit_cf_coef$ordering <- NULL # Drop column used as index
  logit_coef <- logit_cf_coef # Rename df and columns
  names(logit_coef)[names(logit_coef) == "2.5 %"] <- "conf.low"
  names(logit_coef)[names(logit_coef) == "97.5 %"] <- "conf.high"
  rm(logit_cf, logit_cf_coef) # Remove unused stuff
  
  # Retrieve coef table for multilm_interacted with conf.intervals for subsequent plots
  multilm_interacted_cf <- as.data.frame(confint.default(multilm_interacted, level=0.95))
  multilm_interacted_cf$ordering <- 1:nrow(multilm_interacted_cf)
  
  multilm_interacted_coef <- tidy(multilm_interacted) # Get coefficients
  multilm_interacted_coef$ordering <- 1:nrow(multilm_interacted_coef)
  
  multilm_interacted_cf_coef <- merge(multilm_interacted_coef, multilm_interacted_cf, by="ordering", all=TRUE) # Merge coefficients with cf
  multilm_interacted_cf_coef$ordering <- NULL # Drop column used as index
  multilm_interacted_coef <- multilm_interacted_cf_coef # Rename df and columns
  names(multilm_interacted_coef)[names(multilm_interacted_coef) == "2.5 %"] <- "conf.low"
  names(multilm_interacted_coef)[names(multilm_interacted_coef) == "97.5 %"] <- "conf.high"
  rm(multilm_interacted_cf, multilm_interacted_cf_coef) # Remove unused stuff
  
  # Get txt output file
  output_filename = paste(topic, "_lm_output.txt", sep="")
  table_title = paste("Regression models for topic: ", topic, sep="")
  sink(output_filename)
  stargazer(multilm, logit, multilm_interacted, type = "text", title=table_title, dep.var.labels=c("communication (combined mlm)", "interacted (logit)", "communication (conditional mlm)"))
  sink()
  
  # Get LaTeX output file
  output_filename = paste(topic, "_lm_latex_output.txt", sep="")
  table_title = paste("Regression models for topic: ", topic, sep="")
  sink(output_filename)
  stargazer(multilm, logit, multilm_interacted, title=table_title, dep.var.labels=c("communication (combined mlm)", "interacted (logit)", "communication (conditional mlm)"))
  sink()
  
  # Assess multicollinearity (VIF)
  # vif(multilm)
  # vif(multilm_interacted)
  
  # Create list of model outputs per topic
  model_output <- list("topic" = topic, "multilm" = multilm, "multilm_coef" = multilm_coef, "logit" = logit, "logit_coef" = logit_coef, "multilm_interacted" = multilm_interacted, "multilm_interacted_coef" = multilm_interacted_coef)
  return(model_output)
}

writeOutputFile_allModels <- function(all_models_list, topics_list) {
  # Get txt file
  output_filename = "models_output.txt"
  table_title = "Regression models per topic"
  sink(output_filename)
  # combined mlm, logit, conditional mlm
  stargazer(all_models_list, type="text", column.labels = unlist(topics_list), column.separate = c(3, 3, 3, 3, 3), title=table_title, dep.var.labels=c("communication", "interacted", "communication"), initial.zero = FALSE, multicolumn = FALSE)
  sink()
  
  # Get LaTeX file
  output_filename = "models_latex_output.txt"
  table_title = "Regression models per topic"
  sink(output_filename)
  # combined mlm, logit, conditional mlm
  stargazer(all_models_list, column.labels = unlist(topics_list), column.separate = c(3, 3, 3, 3, 3), title=table_title, dep.var.labels=c("communication", "interacted", "communication"), initial.zero = FALSE, multicolumn = FALSE)
  sink()
}

writeOutputFile_multilmModels <- function(all_models_list, topics_list) {
  # Get txt file
  output_filename = "multilm_models_output.txt"
  table_title = "Multiple regression model per topic"
  sink(output_filename)
  # combined mlm
  stargazer(all_models_list, type="text", column.labels = unlist(topics_list), title=table_title, dep.var.labels=c("interactions", "interactions", "interactions", "interactions", "interactions"), initial.zero = FALSE, multicolumn = FALSE)
  sink()
  
  # Get LaTeX file
  output_filename = "multilm_models_latex_output.txt"
  table_title = "Multiple regression model per topic"
  sink(output_filename)
  # combined mlm
  stargazer(all_models_list, column.labels = unlist(topics_list), title=table_title, dep.var.labels=c("interactions", "interactions", "interactions", "interactions", "interactions"), initial.zero = FALSE, multicolumn = FALSE)
  sink()
}

writeOutputFile_logitMultilmModels <- function(all_models_list, topics_list) {
  # Get txt file
  output_filename = "logit_multi_models_output.txt"
  table_title = "Regression models per topic"
  sink(output_filename)
  # combined mlm, logit, conditional mlm
  stargazer(all_models_list, type="text", column.labels = unlist(topics_list), column.separate = c(2, 2, 2, 2, 2), title=table_title, dep.var.labels=c("interacted", "interactions", "interacted", "interactions", "interacted", "interactions", "interacted", "interactions", "interacted", "interactions"), initial.zero = FALSE, multicolumn = FALSE, float.env = "sidewaystable")
  sink()
  
  # Get LaTeX file
  output_filename = "logit_multi_models_latex_output.txt"
  table_title = "Regression models per topic"
  sink(output_filename)
  # combined mlm, logit, conditional mlm
  stargazer(all_models_list, column.labels = unlist(topics_list), column.separate = c(2, 2, 2, 2, 2), title=table_title, dep.var.labels=c("interacted", "interactions", "interacted", "interactions", "interacted", "interactions", "interacted", "interactions", "interacted", "interactions"), initial.zero = FALSE, multicolumn = FALSE, float.env = "sidewaystable")
  sink()
}


#################
### Run below ###
#################

# Loop thourgh metrics files and apply dataModelling function
dataframes_list <- lapply(metrics_files, function(filename) {
  topic <- gsub("_metrics.csv", "", filename, fixed = TRUE)
  nodes_filepath <- paste("../../../assets/derived/", topic, "_metrics.csv", sep="")
  edges_filepath <- paste("../../../assets/derived/edges_", topic, ".csv", sep="")
  df_name <- paste(topic, "_df", sep="")
  df_name <- dataModelling(topic, nodes_filepath, edges_filepath)
  df_info <- list("topic" = topic, "df" = df_name)
  return(df_info)
})

# Loop through dataframes and apply dataAnalysis function
models_output <- lapply(dataframes_list, function(one_element) {
  return(dataAnalysis(one_element$topic, one_element$df))
  print(one_element$topic)
})

# Loop through models output and aggregate them in a models table
# Giant table (all 3 models) - DO NOT USE
# all_models_list <- list()  # Declare empty output list
# for (one_element in models_output) {
#   single_topic_multilm_name <- paste(one_element["topic"], "_multilm_output", sep="")
#   single_topic_logit_name <- paste(one_element["topic"], "_logit_output", sep="")
#   single_topic_multilm_interacted_name <- paste(one_element["topic"], "_multilm_interacted_output", sep="")
#   single_topic_multilm_name  <- one_element["multilm"]
#   single_topic_logit_name  <- one_element["logit"]
#   single_topic_multilm_interacted_name  <- one_element["multilm_interacted"]
#   single_topic_all_models <- list(single_topic_multilm_name, single_topic_logit_name, single_topic_multilm_interacted_name)
#   all_models_list <- c(all_models_list, single_topic_all_models)
#   rm(single_topic_all_models, single_topic_multilm_name, single_topic_logit_name, single_topic_multilm_interacted_name) 
# }  # # Aggregate models output

# Aggregate models table: multilm only
multilm_aggregate_list <- list()  # Declare empty output list
for (one_element in models_output) {
  single_topic_multilm_name <- paste(one_element["topic"], "_multilm_output", sep="")
  single_topic_multilm_name  <- one_element["multilm"]
  single_topic_all_models <- list(single_topic_multilm_name)
  multilm_aggregate_list <- c(multilm_aggregate_list, single_topic_all_models)
  rm(single_topic_all_models, single_topic_multilm_name, one_element)
}  # # Aggregate models output

# Aggregate models table: models 2 and 3
logit_multi_aggregate_list <- list()  # Declare empty output list
for (one_element in models_output) {
  single_topic_logit_name <- paste(one_element["topic"], "_logit_output", sep="")
  single_topic_multilm_interacted_name <- paste(one_element["topic"], "_multilm_interacted_output", sep="")
  single_topic_logit_name  <- one_element["logit"]
  single_topic_multilm_interacted_name  <- one_element["multilm_interacted"]
  single_topic_all_models <- list(single_topic_logit_name, single_topic_multilm_interacted_name)
  logit_multi_aggregate_list <- c(logit_multi_aggregate_list, single_topic_all_models)
  rm(single_topic_all_models, single_topic_logit_name, single_topic_multilm_interacted_name, one_element)
}  # # Aggregate models output

topics_list <- lapply(metrics_files, function(metric_file) {
  topic_from_file <- gsub("_metrics.csv", "", metric_file, fixed = TRUE)
  topic_title <- paste("topic: ", topic_from_file, sep="")
  return(topic_title)
})  # Get current list of topics from dir
# lapply(all_models_list, function(x) x[[1]])  # Remove titles - not really necessary

# Apply writeOutputFile function to the desired lists (multilm_aggregate_list, and logit_multi_aggregate_list)
final_output <- writeOutputFile_multilmModels(multilm_aggregate_list, topics_list)  # Send to stargazer
final_output <- writeOutputFile_logitMultilmModels(logit_multi_aggregate_list, topics_list)  # Send to stargazer

### Compute VIF
vif_array <- list()
for (one_element in models_output) {
  element_multilm <- one_element["multilm"]
  element_logit <- one_element["logit"]
  element_multilm_interacted <- one_element["multilm_interacted"]
  vif_multilm <- vif(element_multilm)
  vif_logit <- vif(element_logit)
  vif_multilm_interacted <- vif(element_multilm_interacted)
  vif_array <- c(vif_array, vif_multilm, vif_logit, vif_multilm_interacted)
  rm(one_element, element_multilm, element_logit, element_multilm_interacted)
}

# Clear all, and save
# save.image(file="forhannes.RData")
rm(list = ls(all.names = TRUE))
gc()

# Misc
tidy(multilm) # Access coefficients
confint(multilm) # Get confidence intervals
sigma(multilm) # Get sigma = RSE in summary
rsquare(multilm, data=df) # R2 as in summary


