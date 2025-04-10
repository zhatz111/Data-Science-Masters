# Full R Code: Newton–Raphson and Fisher Scoring for Poisson Model
# ================================================================

# -------------------------------------------------------------
# Section 1. Simulate Example Data
# -------------------------------------------------------------
# For demonstration purposes, we simulate a dataset with n observations.
# In practice, replace this section with your actual data vectors N, b1, and b2.

set.seed(123)  # for reproducibility

# True parameter values (for simulation)
true_alpha1 <- 0.5  # spill rate per Bbbl for import/export shipments
true_alpha2 <- 0.3  # spill rate per Bbbl for domestic shipments

# Number of years (observations); e.g., 26 years from 1974 to 1999
n <- 26

# Simulate exposure variables (oil shipments in billions of barrels)
# b1: import/export shipments (values between 3 and 6 Bbbl)
# b2: domestic shipments (values between 2 and 4 Bbbl)
b1 <- runif(n, min = 3, max = 6)
b2 <- runif(n, min = 2, max = 4)

# Compute the Poisson means for each observation
lambda_true <- true_alpha1 * b1 + true_alpha2 * b2

# Simulate the number of spills for each year
N <- rpois(n, lambda_true)

# Create a data frame to show the simulated data
years <- 1974:(1974 + n - 1)
data <- data.frame(Year = years, Spills = N, b1 = b1, b2 = b2)
cat("Simulated Data:\n")
print(data)

# -------------------------------------------------------------
# Section 2. Newton–Raphson Implementation
# -------------------------------------------------------------
cat("\n--- Newton–Raphson Method ---\n")

# Starting values for alpha1 and alpha2
alpha_nr <- c(0.001, 0.001)
tol <- 1e-8
max_iter <- 1000

for (iter in 1:max_iter) {
  # Compute current lambda estimates
  lambda_est <- alpha_nr[1] * b1 + alpha_nr[2] * b2
  
  # Compute the score vector (first derivatives)
  score <- c( sum(b1 * (N / lambda_est - 1)),
              sum(b2 * (N / lambda_est - 1)) )
  
  # Compute the observed Hessian (second derivatives)
  H11 <- -sum(b1^2 * N / lambda_est^2)
  H12 <- -sum(b1 * b2 * N / lambda_est^2)
  H22 <- -sum(b2^2 * N / lambda_est^2)
  H <- matrix(c(H11, H12, H12, H22), nrow = 2)
  
  # Newton–Raphson update: alpha_new = alpha_old - H^{-1} %*% score
  delta <- solve(H, score)
  alpha_new <- alpha_nr - delta
  
  # Check convergence: if the change is less than tol, break out of the loop
  if (sqrt(sum((alpha_new - alpha_nr)^2)) < tol) {
    alpha_nr <- alpha_new
    cat("Newton–Raphson converged in", iter, "iterations.\n")
    break
  }
  
  # Update parameters for next iteration
  alpha_nr <- alpha_new
}

cat("Newton–Raphson MLEs:\n")
cat("alpha1 =", alpha_nr[1], "\n")
cat("alpha2 =", alpha_nr[2], "\n")

# -------------------------------------------------------------
# Section 3. Fisher Scoring Implementation
# -------------------------------------------------------------
cat("\n--- Fisher Scoring Method ---\n")

# Starting values for alpha1 and alpha2
alpha_fs <- c(0.001, 0.001)
tol <- 1e-8
max_iter <- 1000

for (iter in 1:max_iter) {
  # Compute current lambda estimates
  lambda_est <- alpha_fs[1] * b1 + alpha_fs[2] * b2
  
  # Compute the score vector (first derivatives)
  score <- c( sum(b1 * (N / lambda_est - 1)),
              sum(b2 * (N / lambda_est - 1)) )
  
  # Compute the expected Fisher Information matrix:
  # I(alpha) = sum(1/lambda_i * [b1_i^2, b1_i*b2_i; b1_i*b2_i, b2_i^2])
  I11 <- sum(b1^2 / lambda_est)
  I12 <- sum(b1 * b2 / lambda_est)
  I22 <- sum(b2^2 / lambda_est)
  I_mat <- matrix(c(I11, I12, I12, I22), nrow = 2)
  
  # Fisher scoring update: alpha_new = alpha_old + I^{-1} %*% score
  delta <- solve(I_mat, score)
  alpha_new <- alpha_fs + delta
  
  # Check convergence: if the change is less than tol, break out of the loop
  if (sqrt(sum((alpha_new - alpha_fs)^2)) < tol) {
    alpha_fs <- alpha_new
    cat("Fisher Scoring converged in", iter, "iterations.\n")
    break
  }
  
  # Update parameters for next iteration
  alpha_fs <- alpha_new
}

cat("Fisher Scoring MLEs:\n")
cat("alpha1 =", alpha_fs[1], "\n")
cat("alpha2 =", alpha_fs[2], "\n")
