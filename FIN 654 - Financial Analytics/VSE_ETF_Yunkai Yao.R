## Step2.1 Using for loop to download 11 ETFs
nmlist<-c('XLK','XLV','XLF','XLY', 'XLP',
          'XLU','XLE','XLC','XLI','XLRE','XLB')
## Check the 1st element in nmlist
nmlist[1]

Returns<-list()
for (i in 1: length(nmlist)){
  getSymbols(nmlist[i], from='2020-10-27',to='2023-10-27')
  ret<-dailyReturn(Ad(get(nmlist[i])))
  Returns[[i]]<-ret
}

class(Returns)

rt <- cbind(Returns[[1]], Returns[[2]])

returns <- do.call(cbind, Returns)
class(returns)

returns <- round(returns, digits = 4)
colnames(returns) <- nmlist
View(returns)

## Step 2.2 Compute Efficient Frontier
#install.packages("fPortfolio")
library(fPortfolio)

returns_series<-as.timeSeries(returns)

specEF<-portfolioSpec()
setRiskFreeRate(specEF)<-0.02/252

returns_series<-as.timeSeries(returns)
specEF<-portfolioSpec()
setRiskFreeRate(specEF)<-0.02/252
frontier<-portfolioFrontier(returns_series,specEF)

View(frontier)

frontier_points<-frontierPlot(frontier, pch = 19)
grid()

View(frontier_points)
class(frontier_points)

EF_point<-singleAssetPoints(frontier, pch=19,cex=1.5, col="orange")
class(EF_point)
View(EF_point)

text( y=EF_point[,"targetReturn"],
      x=EF_point[,"targetRisk"],
      labels=row.names(EF_point),
      pos=4,cex=1)

minvariancePoints(frontier,
                  pch = 19,cex=1.5, col = "red")

tangencyLines(frontier,
              lty=1,lwd=4,col = "blue")

tangencyPoints(frontier,
               pch = 19, cex=1.5, col = "green")

## Step3.1: Compute financial indicators of XLK
#install.packages("PerformanceAnalytics")
library(PerformanceAnalytics)

m_xlk<-mean(returns[,'XLK'])
s_xlk<-sd(returns[,'XLK'])
SR_xlk<-m_xlk/s_xlk
varisk_xlk<-quantile(returns[,'XLK'],probs = c(0.05))
es_xlk<-ES(returns[,'XLK'],p=0.05,method = 'historical')

colname<-c("mean", "std", "SR","VaR","ES")
stats<-matrix(NA,ncol = 5,nrow = 11,dimnames = list(nmlist, colname))
for (i in 1:length(nmlist)) {
  value<-returns[,nmlist[i]]
  m = mean(value)
  s = sd(value)
  SR = m/s
  varisk = quantile(value,probs = c(0.05))
  es = ES(value,p=0.05,method = 'historical')
  stats[i,1]<-m
  stats[i,2]<-s
  stats[i,3]<-SR
  stats[i,4]<-varisk
  stats[i,5]<-es
}

View(stats)

ETF8<-returns[,-which(colnames(returns) %in% c("XLV","XLP","XLI"))]

myETF<-ETF8[,which(colnames(ETF8) %in% c("XLE","XLF","XLK"))]

#install.packages("fPortfolio")
library(fPortfolio)
myETF_Series<-as.timeSeries(myETF)

specPort<-portfolioSpec()
setRiskFreeRate(specPort)<-0.02/252

minvar<-minvariancePortfolio(myETF_Series,specPort)
minvar

maxSharpe<-tangencyPortfolio(myETF_Series,specPort)
maxSharpe
# 31.49% captial invest to XLE
# 58.4% captial invest to XLF
# 10.11% captial invest to XLK

# compute y0*
y0 <- (0.0016-(0.02/252))/(1.06*0.0179^2)
y0

# market price of XLE, XLF, XLK
XLEprice <- 84.63
XLFprice <- 31.45
XLKprice <- 161.12

# set networth
networth <- 100000

# compute my personal shares
XLEshare <- (networth*y0*0.1551)/XLEprice
XLEshare 

XLFshare <- (networth*y0*0.0000)/XLFprice
XLFshare

XLKshare <- (networth*y0*0.8449)/XLKprice
XLKshare 

