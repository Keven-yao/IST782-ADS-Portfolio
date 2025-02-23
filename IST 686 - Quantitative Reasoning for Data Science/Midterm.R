library(tidyverse)

Time <- read.csv('/Users/yaoyunkai/Desktop/IST 686/MIDTERM - March 6th/Time.csv')
set.seed(3618)
myData<-Time[sample(1:nrow(Time), 100, replace=FALSE),]

#a
str(myData)
summary(myData$time)

#b
boxplot(time ~ home, data = myData)

#c
owners <- subset(myData, home == TRUE)$time
non_owners <- subset(myData, home == FALSE)$time
t_test <- t.test(owners, non_owners, var.equal = TRUE)
print(t_test)

conf_int_owners <- t.test(owners, conf.level = 0.95)$conf.int
print(conf_int_owners)

conf_int_non_owners <- t.test(non_owners, conf.level = 0.95)$conf.int
print(conf_int_non_owners)
