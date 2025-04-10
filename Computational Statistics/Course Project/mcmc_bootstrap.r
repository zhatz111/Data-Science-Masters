# --------------------- Load Libraries ---------------------
library(dplyr)
library(ggplot2)
library(pROC)
library(caret)

# --------------------- Load and Prepare Data ---------------------
data <- read.csv("C:\\Users\\zhatz\\Documents\\GitHub\\Data-Science-Masters\\Computational Statistics\\Course Project\\creditcard.csv")
data <- data[!duplicated(data), ] # Remove duplicates
data$Class <- as.factor(data$Class)
levels(data$Class) <- c("0", "1")

# Drop Time column (not PCA-transformed, not used)
data <- data %>% select(-Time)

# Scale predictors (excluding Class)
data[,-ncol(data)] <- scale(data[,-ncol(data)])

# --------------------- Metropolis-Hastings for Feature Selection ---------------------
features <- colnames(data)[colnames(data) != "Class"]
n_iter <- 200
selected_features <- character(n_iter)

set.seed(123)
current_features <- sample(features, 5)
current_formula <- as.formula(paste("Class ~", paste(current_features, collapse = "+")))
current_model <- glm(current_formula, data = data, family = "binomial")
current_ll <- logLik(current_model)

for (i in 1:n_iter) {
  proposed_features <- current_features
  swap <- sample(features, 1)
  
  if (swap %in% proposed_features) {
    proposed_features <- setdiff(proposed_features, swap)
  } else {
    proposed_features <- union(proposed_features, swap)
  }
  
  if (length(proposed_features) == 0) next
  
  prop_formula <- as.formula(paste("Class ~", paste(proposed_features, collapse = "+")))
  prop_model <- glm(prop_formula, data = data, family = "binomial")
  prop_ll <- logLik(prop_model)
  
  accept_ratio <- exp(prop_ll - current_ll)
  if (runif(1) < accept_ratio) {
    current_features <- proposed_features
    current_ll <- prop_ll
  }
  selected_features[i] <- paste(current_features, collapse = ",")
}

# --------------------- Analyze Feature Frequencies ---------------------
top_features <- sort(table(unlist(strsplit(selected_features, ","))), decreasing = TRUE)
cat("Top selected features:\n")
print(head(top_features, 10))
selected_vars <- names(head(top_features, 15))
formula <- as.formula(paste("Class ~", paste(selected_vars, collapse = "+")))

# --------------------- Stratified Bootstrap AUC Evaluation (MCMC-Selected) ---------------------
set.seed(123)
auc_mcmc <- numeric(100)

for (i in 1:100) {
  idx <- createDataPartition(data$Class, p = 0.7, list = FALSE)
  train <- data[idx, ]
  test <- data[-idx, ]
  model <- glm(formula, data = train, family = "binomial")
  prob <- predict(model, newdata = test, type = "response")
  roc_obj <- roc(as.numeric(as.character(test$Class)), prob)
  auc_mcmc[i] <- auc(roc_obj)
}

# --------------------- Stratified Bootstrap AUC Evaluation (Full Model) ---------------------
auc_full <- numeric(100)
full_formula <- as.formula(paste("Class ~", paste(features, collapse = "+")))

for (i in 1:100) {
  idx <- createDataPartition(data$Class, p = 0.7, list = FALSE)
  train <- data[idx, ]
  test <- data[-idx, ]
  model <- glm(full_formula, data = train, family = "binomial")
  prob <- predict(model, newdata = test, type = "response")
  roc_obj <- roc(as.numeric(as.character(test$Class)), prob)
  auc_full[i] <- auc(roc_obj)
}

# --------------------- AUC Boxplot Comparison ---------------------
df_auc <- data.frame(
  AUC = c(auc_mcmc, auc_full),
  Model = rep(c("MCMC-Selected", "Full-Feature"), each = 100)
)

ggplot(df_auc, aes(x = Model, y = AUC, fill = Model)) +
  geom_boxplot(alpha = 0.7) +
  labs(title = "AUC Comparison: MCMC-Selected vs Full-Feature Logistic Regression",
       x = "Model Type", y = "AUC Score") +
  theme_minimal()

# --------------------- AUC Summary ---------------------
cat("\n--- MCMC AUC Summary ---\n")
cat("Average AUC:", mean(auc_mcmc), "\n")
cat("Standard Deviation:", sd(auc_mcmc), "\n")
print(quantile(auc_mcmc, c(0.025, 0.975)))

cat("\n--- Full-Feature AUC Summary ---\n")
cat("Average AUC:", mean(auc_full), "\n")
cat("Standard Deviation:", sd(auc_full), "\n")
print(quantile(auc_full, c(0.025, 0.975)))

# --------------------- Final Model Metrics ---------------------
final_model <- glm(formula, data = data, family = "binomial")
prob_pred <- predict(final_model, type = "response")
pred_class <- ifelse(prob_pred > 0.5, 1, 0)
conf_matrix <- confusionMatrix(factor(pred_class), data$Class)
print(conf_matrix)

# --------------------- Feature Inclusion Probability Plot ---------------------
inclusion_probs <- prop.table(table(unlist(strsplit(selected_features, ","))))
df_plot <- data.frame(
  Feature = names(inclusion_probs),
  InclusionProb = as.numeric(inclusion_probs)
)

ggplot(df_plot, aes(x = reorder(Feature, InclusionProb), y = InclusionProb)) +
  geom_bar(stat = "identity", fill = "steelblue") +
  coord_flip() +
  labs(title = "Feature Inclusion Probabilities via Metropolis-Hastings",
       x = "Feature", y = "Inclusion Probability") +
  theme_minimal()

# --------------------- ROC Curves ---------------------

# Predict using final full-feature model
final_full_model <- glm(full_formula, data = data, family = "binomial")
prob_pred_full <- predict(final_full_model, type = "response")
roc_full <- roc(as.numeric(as.character(data$Class)), prob_pred_full)

# Predict using final MCMC-selected model
final_mcmc_model <- glm(formula, data = data, family = "binomial")
prob_pred_mcmc <- predict(final_mcmc_model, type = "response")
roc_mcmc <- roc(as.numeric(as.character(data$Class)), prob_pred_mcmc)

# Plot ROC curve for full-feature model
plot(roc_full,
     legacy.axes = TRUE,
     col = "darkgray",
     lwd = 2,
     main = "ROC Curve: Full vs MCMC-Selected Model",
     xlab = "False Positive Rate (1 - Specificity)",
     ylab = "True Positive Rate (Sensitivity)"
)

# Add ROC curve for MCMC-selected model
lines(roc_mcmc, col = "darkred", lwd = 2)

# Add diagonal reference line
abline(a = 0, b = 1, lty = 2, col = "gray")

# Add legend with AUC values
legend("bottomright",
       legend = c(paste0("Full Model AUC = ", round(auc(roc_full), 3)),
                  paste0("MCMC Model AUC = ", round(auc(roc_mcmc), 3))),
       col = c("darkgray", "darkred"),
       lwd = 2,
       bty = "n"
)

# Optional: add grid
grid()
