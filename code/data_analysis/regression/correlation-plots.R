library(ggpubr)
library(tikzDevice)
library(Hmisc)
library(corrplot)

# 1. Script for the correlation matrix - get data from looping model (dataframes_list)
for (one_element in dataframes_list) {
numeric_values <- one_element[["df"]][ , 7:19] # Get only numeric variables from df
numeric_values$modularity_class <- NULL # Drop modularity from the matrix
# 1. Rename variables (column headers)
names(numeric_values)[names(numeric_values) == "Degree"] <- "degree"
names(numeric_values)[names(numeric_values) == "Eccentricity"] <- "eccentricity"
names(numeric_values)[names(numeric_values) == "closnesscentrality"] <- "closeness_centrality"
names(numeric_values)[names(numeric_values) == "harmonicclosnesscentrality"] <- "harmonic_closeness_centrality"
names(numeric_values)[names(numeric_values) == "betweenesscentrality"] <- "betweeness_centrality"
corr_matrix <- cor(numeric_values) # Construct corr matrix, add method="spearman" for rho
# 1. Graph correlations
col <- colorRampPalette(c("#BB4444", "#EE9988", "#FFFFFF", "#77AADD", "#4477AA"))
corrplot(corr_matrix, title=one_element[["topic"]], method="color", col=col(200), type="lower", tl.col = "black", tl.cex=0.8, addCoef.col = "black", number.cex = 0.7)
rm(numeric_values, one_element)
}

#----
# 2. Function to flatten corr matrix
flattenCorrMatrix <- function(cormat, pmat) {
  ut <- upper.tri(cormat)
  data.frame(
    row = rownames(cormat)[row(cormat)[ut]],
    column = rownames(cormat)[col(cormat)[ut]],
    cor  =(cormat)[ut],
    p = pmat[ut]
  )
}

# 2. Flat Correlation matrix
numeric_values <- dataframes_list[[3]][["df"]][ , c(7:19, 22:34)] # Get only numeric variables from df
topic_correlations <- rcorr(as.matrix(numeric_values)) # Construct corr matrix, add type="spearman" for rho
flat_topic_corr_matrix <- flattenCorrMatrix(topic_correlations$r, topic_correlations$P)
rm(numeric_values, topic_correlations)

#----
#3. Manual Pearson correlations
outdegree_pearson_corr <- cor.test(dataframes_list[[2]][["df"]][["outdegree"]],dataframes_list[[2]][["df"]][["u2_outdegree"]],method="pearson")
eigen_pearson_corr <- cor.test(dataframes_list[[2]][["df"]][["eigencentrality"]],dataframes_list[[2]][["df"]][["u2_eigencentrality"]],method="pearson")
clustering_pearson_corr <- cor.test(dataframes_list[[2]][["df"]][["clustering"]],dataframes_list[[2]][["df"]][["u2_clustering"]],method="pearson")
outdegree_pearson_corr
eigen_pearson_corr
clustering_pearson_corr

#----
# NO - tikzDevice to output R plots to LaTeX
options(tikzLatex="E:/Users/u336937/AppData/Local/Programs/MiKTeX 2.9/miktex/bin/x64/pdflatex.exe")
tikz(file="indegree-eigen-corr-plot.tex", width=7, height=6)
# Plot here
dev.off()

# 4. Bivariate Plots
ggplot(dataframes_list[[2]][["df"]], aes(x=indegree, y=eigencentrality)) +
  geom_point(colour="red") +
  geom_smooth(method = lm) +
  # geom_errorbar(aes(ymin = conf.low, ymax = conf.high), width=0.5) +
  labs(title = "Correlation for topic: populism") + 
  # scale_y_continuous() + 
  # coord_flip() + 
  theme_bw()

correlation_plot2 <- ggplot(dataframes_list[[5]][["df"]], aes(x=indegree, y=outdegree)) +
  geom_point(colour="red") +
  geom_smooth(method = lm) +
  # geom_errorbar(aes(ymin = conf.low, ymax = conf.high), width=0.5) +
  labs(title = "Correlation for topic: unemployment") + 
  # scale_y_continuous() + 
  # coord_flip() + 
  theme_bw()
correlation_plot2

correlation_plot3 <- ggplot(dataframes_list[[2]][["df"]], aes(x=closnesscentrality, y=eigencentrality)) +
  geom_point(colour="red") +
  geom_smooth(method = lm) +
  # geom_errorbar(aes(ymin = conf.low, ymax = conf.high), width=0.5) +
  labs(title = "Correlation for topic: populism") + 
  # scale_y_continuous() + 
  # coord_flip() + 
  theme_bw()
correlation_plot3
