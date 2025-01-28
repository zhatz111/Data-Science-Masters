
# Question 1
print("Start of Question 1")

data_char <- read.table("Computational Statistics/Module 1/favorite.data", header = FALSE)
data_numeric <- as.numeric(data_char$V1)

data_mean <- mean(data_numeric) # a
data_median <- median(data_numeric) # b
data_std <- sd(data_numeric) # c
data_min <- min(data_numeric) # d
data_max <- max(data_numeric) # e
hist(data_numeric, col="green", border="black") # f

print(data_mean)
print(data_median)
print(data_std)
print(data_min)
print(data_max)


# Question 2
print("Start of Question 2")

rand_samples = rnorm(10000, 1, sqrt(2))

# 2a
hist(rand_samples, col="pink", border="black")

# 2b
rand_mean <- mean(rand_samples)
rand_median <- median(rand_samples)
rand_std <- sd(rand_samples)

print(rand_mean)
print(rand_median)
print(rand_std)


# Question 3
print("Start of Question 3")

vector_r = seq(from = 5, to = 160, by = 5)
vector_b = seq(from = 56, to = 87, by = 1)
vector_d = vector_r * vector_b

# 3a
print(vector_d[17])
print(vector_d[18])
print(vector_d[19])

# 3b
print(vector_d[vector_d < 2000])

# 3c
print(length(vector_d[vector_d > 6000]))


# Question 4
print("Start of Question 4")

perfect_square <- function(x) {
    squares_seq = seq(from=1, to=x, by=1)
    total <- 0
    squares_list = list()
    count <- 1
    for (i in squares_seq) {
        i_sqrt = sqrt(i)
        if (i_sqrt%%1==0) {
            total <- total + i
            squares_list[[count]] <- i
            count <- count + 1
        }
    }
    output <- list(total, squares_list)
    return(output)
}

# 4a
print(perfect_square(100)[1])

# 4b
print(perfect_square(100000)[1])



# Question 5
print("Start of Question 5")

# 5a
list_500 = perfect_square(500)[2]
vector_500 <- unlist(list_500, use.names=FALSE)
print(vector_500)


# 5b
list_100000 = perfect_square(100000)[2]
vector_100000 <- unlist(list_100000, use.names=FALSE)
matrix_100000 <- matrix(vector_100000, ncol = 4)
print(matrix_100000)

# 5c
print(matrix_100000[15,3])


# Question 6
print("Start of Question 6")


x <- seq(from = -pi, to = pi, length.out = 50)  
y1 <- sin(x)
y2 <- cos(x)

# 6a
plot(x, y1, col="blue", cex=3)

# 6b and 6c
plot(x, y2, type="l", col="blue", lwd=3)
lines(c(-3, 3), c(-1, 1), col="red", lwd=3)
