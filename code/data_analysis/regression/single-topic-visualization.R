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
topic <- "brexit" 
nodes_filepath <- paste("../../../assets/derived/", topic, "_metrics.csv", sep="")
edges_filepath <- paste("../../../assets/derived/edges_", topic, ".csv", sep="")

options(scipen=999)

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

## Model below

multilm <- lm(communication ~ closnesscentrality + betweenesscentrality + eigencentrality + clustering + weighted_outdegree*u2_weighted_indegree + closnesscentrality*u2_closnesscentrality + eigencentrality*u2_eigencentrality + eigencentrality*u2_weighted_indegree + clustering*u2_clustering, data=df)
summary(multilm)

tidy_coef <- tidy(multilm, conf.int=TRUE)

cf <- as.data.frame(confint.default(multilm, level=0.95))
cf$ordering <- 1:nrow(cf)

coef <- tidy(multilm)
coef$ordering <- 1:nrow(coef)

cf_coef <- merge(coef, cf, by="ordering", all=TRUE)
cf_coef$ordering <- NULL
coef <- cf_coef
names(coef)[names(coef) == "2.5 %"] <- "conf.low"
names(coef)[names(coef) == "97.5 %"] <- "conf.high"
rm(cf, cf_coef)


ggplot(coef, aes(term, estimate))+
  geom_point()+
  geom_pointrange(aes(ymin = conf.low, ymax = conf.high))+
  labs(title = "coef")+ coord_flip()