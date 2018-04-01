source('data.R')
require(boot)

normalize_vector <- function(x) {x / sqrt(sum(x^2))}

mean_squared_error <- function(y, yhat){mean((yhat - y)^2)}

sentiment.boot.fun <- function(aspect_opinion, indices){
  aspect_opinion <- aspect_opinion[indices,]
  
  
  sentiment_results_msqe <- mean_squared_error(aspect_opinion$overall, aspect_opinion$sentiment)
  return(sentiment_results_msqe)
}

do_bootsrap <- function(aspect_opinion, boot.fun, R){
  set.seed(1)
  msqe <- boot(data=aspect_opinion, statistic=boot.fun, R=R)
  return(msqe)
}


aspect_opinion <- unique(aspect_opinion[,c('index', 'overall', 'sentiment', 'token')])
aspect_opinion_sentiment_aggr <- aspect_opinion
aspect_opinion_sentiment_aggr <- aggregate(aspect_opinion_sentiment_aggr$sentiment, by=list(aspect_opinion_sentiment_aggr$index), sum)
aspect_opinion_rating_aggr <- aggregate(aspect_opinion$overall, by=list(aspect_opinion$index), mean)
nrow(aspect_opinion_sentiment_aggr) == nrow(aspect_opinion_rating_aggr) # TRUE

sentiment_results <- data.frame(sentiment = normalize_vector(aspect_opinion_sentiment_aggr$x), overall = normalize_vector(aspect_opinion_rating_aggr$x))

sentiment_boot_results <- do_bootsrap(sentiment_results, sentiment.boot.fun, 1000)