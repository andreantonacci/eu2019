# Script to graph regression coefficients and their SE - Get data from looping model (dataframes_list)
# Transform the giant list to a df
df_coef <- data.frame(term = character(),
                      topic = character(),
                      model = character(),
                      estimate = double(),
                      std.error = double(),
                      statistic = double(),
                      p.value = double(),
                      conf.low = double(),
                      conf.high = double()
)
for (element in models_output) {
   element_multilm_coef <- as.data.frame(element["multilm_coef"])
   element_logit_coef <- as.data.frame(element["logit_coef"])
   element_multilm_interacted_coef <- as.data.frame(element["multilm_interacted_coef"])
   
   topic_name <- element["topic"][[1]]
   
   for (i in 1:8) { # Loop through rows of the coefficient tables
      row1 <- list(term = element_multilm_coef[i+1, 1], topic = topic_name, model = "multilm")
      row1 <- append(row1, as.list(element_multilm_coef[i+1, 2:7]))
      row1 <- as.data.frame(row1)
      names(row1) <- c("term", "topic", "model", "estimate", "std.error", "statistic", "p.value", "conf.low", "conf.high")
      
      row2 <- list(element_logit_coef[i+1, 1], topic_name, "logit")
      row2 <- append(row2, as.list(element_logit_coef[i+1, 2:7]))
      row2 <- as.data.frame(row2)
      names(row2) <- c("term", "topic", "model", "estimate", "std.error", "statistic", "p.value", "conf.low", "conf.high")
      
      row3 <- list(element_multilm_interacted_coef[i+1, 1], topic_name, "multilm_interacted")
      row3 <- append(row3, as.list(element_multilm_interacted_coef[i+1, 2:7]))
      row3 <- as.data.frame(row3)
      names(row3) <- c("term", "topic", "model", "estimate", "std.error", "statistic", "p.value", "conf.low", "conf.high")
      
      df_coef <- rbind(df_coef, row1, row2, row3)
   }
}
rm(row1, row2, row3, element, element_logit_coef, element_multilm_coef, element_multilm_interacted_coef)

# df_coef$estimate=as.numeric(levels(df_coef$estimate))[df_coef$estimate]

# Plots
# All variables
ggplot(df_coef, aes(topic, estimate, color=model, shape=model)) +
   geom_point() +
   geom_errorbar(aes(ymin = conf.low, ymax = conf.high), width=0.5) +
   labs(title = "Models coefficients per topic", x = "Topic", y = "Coefficients and SE", colour = "Model", shape = "Model") + scale_y_continuous() + coord_flip() + facet_wrap(~ term, scales = "free") + theme_bw()

# Single variable plot: subset[subset$row == value, subset$column == value]
ggplot(df_coef[df_coef$term == "eigencentrality" | df_coef$term == "u2_eigencentrality",], aes(topic, estimate, color=model, shape=model)) +
   geom_point() +
   geom_errorbar(aes(ymin = conf.low, ymax = conf.high), width=0.5) +
   labs(title = "Models coefficients per topic", x = "Topic", y = "Coefficients and SE", colour = "Model", shape = "Model") + scale_y_continuous() + coord_flip() + facet_wrap(~ term, scales = "free") + theme_bw()
