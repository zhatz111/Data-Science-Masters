library(ggplot2)

gibbs_sampler <- function(rho, num_samples, burn_in) {
  x1 <- 0
  x2 <- 0
  samples <- matrix(0, nrow = num_samples, ncol = 2)
  
  for (i in 1:(num_samples + burn_in)) {
    x1 <- rnorm(1, mean = rho * x2, sd = sqrt(1 - rho^2))
    x2 <- rnorm(1, mean = rho * x1, sd = sqrt(1 - rho^2))
    
    if (i > burn_in) {
      samples[i - burn_in, ] <- c(x1, x2)
    }
  }
  
  return(as.data.frame(samples))
}

# Define parameters
rhos <- c(0, 0.1, 0.2, 0.3, 0.4, 0.5)
burn_in_values <- c(0, 100, 1000)
num_samples <- 5000

gibbs_results <- data.frame()

# Generate samples for different rho and burn-in values
for (rho in rhos) {
  for (burn_in in burn_in_values) {
    samples <- gibbs_sampler(rho, num_samples, burn_in)
    samples$rho <- rho
    samples$burn_in <- burn_in
    gibbs_results <- rbind(gibbs_results, samples)
  }
}

# Plot results
print(
  ggplot(gibbs_results, aes(V1, V2)) +
    geom_point(alpha = 0.3, size = 0.5) +
    facet_grid(rho ~ burn_in, labeller = label_both) +
    theme_minimal() +
    labs(title = "Gibbs Sampling for Bivariate Normal Distribution",
         x = "X1", y = "X2") +
    theme(plot.title = element_text(hjust = 0.5))
)
