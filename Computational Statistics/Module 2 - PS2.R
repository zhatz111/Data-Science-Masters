# Data
x <- c(1.77, -0.23, 2.76, 3.80, 3.47, 56.75, -1.34, 4.24, -2.44, 3.29, 
       3.71, -2.40, 4.53, -0.07, -1.05, -13.87, -2.53, -1.75, 0.27, 43.21)

# Log-likelihood function for Cauchy(θ, 1)
loglik_cauchy <- function(theta, x) {
  n <- length(x)
  -n * log(pi) - sum(log(1 + (x - theta)^2))
}

# First and second derivatives of the log-likelihood
dloglik_cauchy <- function(theta, x) {
  sum(2 * (x - theta) / (1 + (x - theta)^2))
}

d2loglik_cauchy <- function(theta, x) {
  sum((2 - 2 * (x - theta)^2) / (1 + (x - theta)^2)^2)
}

# Part (a): Graph the log-likelihood function and apply Newton-Raphson
theta_vals <- seq(min(x) - 5, max(x) + 5, length.out = 100)
loglik_vals <- sapply(theta_vals, function(theta) loglik_cauchy(theta, x))

plot(theta_vals, loglik_vals, type = "l", col = "blue",
     main = "Log-Likelihood Function for Cauchy(θ, 1)",
     xlab = "θ", ylab = "Log-Likelihood")

newton_raphson <- function(x, start, max_iter = 100, tol = 1e-6) {
  theta <- start
  for (i in 1:max_iter) {
    grad <- dloglik_cauchy(theta, x)
    hess <- d2loglik_cauchy(theta, x)
    if (abs(hess) < 1e-10) break
    theta_new <- theta - grad / hess
    if (abs(theta_new - theta) < tol) return(theta_new)
    theta <- theta_new
  }
  return(theta)
}

# Run Newton-Raphson for different starting points
start_points <- c(-11, -1, 0, 1.5, 4, 4.7, 7, 8, 38)
nr_results <- sapply(start_points, function(start) newton_raphson(x, start))

cat("\n(a) Newton-Raphson Results:\n")
for (i in seq_along(start_points)) {
  cat("Start:", start_points[i], "→ MLE:", nr_results[i], "\n")
}

# Part (b): Bisection method
bisection_method <- function(x, a, b, tol = 1e-6) {
  while (abs(b - a) > tol) {
    c <- (a + b) / 2
    if (dloglik_cauchy(c, x) * dloglik_cauchy(a, x) < 0) {
      b <- c
    } else {
      a <- c
    }
  }
  return((a + b) / 2)
}

# Run bisection method with different intervals
bisection_results <- c(
  bisection_method(x, -1, 1),
  bisection_method(x, -10, 10),
  bisection_method(x, -100, 100)
)

cat("\n(b) Bisection Results:\n")
cat("Interval [-1, 1]:", bisection_results[1], "\n")
cat("Interval [-10, 10]:", bisection_results[2], "\n")
cat("Interval [-100, 100]:", bisection_results[3], "\n")

# Part (c): Fixed-point iteration
fixed_point_iteration <- function(x, theta_start, alpha, tol = 1e-6, max_iter = 100) {
  theta <- theta_start
  for (i in 1:max_iter) {
    theta_new <- theta + alpha * dloglik_cauchy(theta, x)
    if (abs(theta_new - theta) < tol) break
    theta <- theta_new
  }
  return(theta)
}

alphas <- c(1, 0.64, 0.25)
fps_results <- sapply(alphas, function(alpha) fixed_point_iteration(x, -1, alpha))

cat("\n(c) Fixed-Point Iteration Results:\n")
for (i in seq_along(alphas)) {
  cat("Alpha:", alphas[i], "→ MLE:", fps_results[i], "\n")
}

# Part (d): Secant method
secant_method <- function(f, x0, x1, tol = 1e-6, max_iter = 100) {
  for (i in 1:max_iter) {
    f_x0 <- f(x0)
    f_x1 <- f(x1)
    if (abs(f_x1 - f_x0) < tol) break
    x2 <- x1 - f_x1 * (x1 - x0) / (f_x1 - f_x0)
    if (abs(x2 - x1) < tol) return(x2)
    x0 <- x1
    x1 <- x2
  }
  return(x1)
}

secant_results <- c(
  secant_method(function(theta) dloglik_cauchy(theta, x), -2, -1),
  secant_method(function(theta) dloglik_cauchy(theta, x), -3, 3)
)

cat("\n(d) Secant Method Results:\n")
cat("Start (-2, -1):", secant_results[1], "\n")
cat("Start (-3, 3):", secant_results[2], "\n")

# Part (e): Comparison on Normal(θ, 1) data
set.seed(42)
normal_sample <- rnorm(20, mean = 5, sd = 1)

nr_normal <- newton_raphson(normal_sample, 5)
bis_normal <- bisection_method(normal_sample, 4, 6)
fps_normal <- fixed_point_iteration(normal_sample, 5, 0.5)
sec_normal <- secant_method(function(theta) dloglik_cauchy(theta, normal_sample), 4, 6)

cat("\n(e) Normal(θ, 1) Data Results:\n")
cat("Newton-Raphson MLE:", nr_normal, "\n")
cat("Bisection MLE:", bis_normal, "\n")
cat("Fixed-Point MLE:", fps_normal, "\n")
cat("Secant MLE:", sec_normal, "\n")


# Problem 2b
dfunc <- function(x) {
  return (-x^3 + x - 1)
}

d2func <- function(x) {
  return (-3*x^2 + 1)
}

newton_raphson_2 <- function(start, max_iter = 100, tol = 1e-6) {
  x <- start
  count <- 0
  for (i in 1:max_iter) {
    grad <- dfunc(x)
    hess <- d2func(x)
    x_new <- x - grad / hess
    if (abs(x_new - x) < tol) return(list(x_new, count))
    x <- x_new
    count <- count + 1
  }
  return(list(x, count))
}

result <- newton_raphson_2(2)

cat("\n(2b) Newton-Raphson Result:\n")
cat("Newton-Raphson:", result[[1]], "\n")
cat("Number of Iterations:", result[[2]], "\n")