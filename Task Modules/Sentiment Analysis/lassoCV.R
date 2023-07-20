library(glmnet)
train = read.csv('train.csv')
price = read.csv('price.csv')
train[,1] = price$price
names(train)[1] = "price"
cvfit <- glmnet::cv.glmnet(as.matrix(train[,-1]), train$price)
coefficients = coef(cvfit, s = "lambda.1se")
plot(cvfit)

lassocoef <- data.frame(name = coefficients@Dimnames[[1]][coefficients@i + 1], coefficient = coefficients@x)
X = train[,as.character(lassocoef$name[-1])]
Y = train$price

idx = sort(sample(dim(X)[1], dim(X)[1]/2, replace = FALSE))

