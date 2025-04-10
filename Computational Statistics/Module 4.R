# Define the function to integrate
f <- function(x) {
  4 * sqrt(1 - x^2)
}

# Number of iterations
N <- 5000  

# Generate random samples from uniform distribution in [0,1]
x_random <- runif(N, min = 0, max = 1)

# Evaluate the function at these points
f_values <- f(x_random)

# Estimate the integral using Monte Carlo method
integral_estimate <- mean(f_values)

# Print the result
cat("Monte Carlo estimate of the integral with 5000 iterations:", integral_estimate, "\n")