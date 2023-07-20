train = read.csv("train.csv")
price = read.csv("price.csv")

train = train[,-1]
train = data.frame(scale(train))
price$price = exp(price$price)
train$price = price$price

library(pscl)
reg = zeroinfl(number_of_reviews_ltm ~ price, dist = "poisson", data = train)
summary(reg)

reg2 = zeroinfl(number_of_reviews_ltm ~ 1, dist = "poisson", data = train)
summary(reg2)

library(MASS)
step.reg = step(reg2, scope = ~ price + host_is_superhost + host_response_rate + review_scores_cleanliness
                 + guests_included,
                direction = "forward", trace = 0)
summary(step.reg)
