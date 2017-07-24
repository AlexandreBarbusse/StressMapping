setwd("C:/Stage_Shanghai/Scripts")
mydata <- read.csv('improved_results2.csv',header=T,na.strings=c(""))
mydata$green_criteria <- factor(mydata$green_criteria)
mydata$variable_y <- factor(mydata$variable_y)
library(vcd)
table_green <- table(mydata$variable_y,mydata$green_criteria)
table_green
labs <- round(prop.table(table_green, 2),2)
labs
chisq.test(table_green) 