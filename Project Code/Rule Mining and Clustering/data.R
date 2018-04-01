get_portion_of_sample <- function(data, portion){
  ## 75% of the sample size
  smp_size <- floor(portion * nrow(data))
  
  ## set the seed to make your partition reproductible
  set.seed(123)
  train_ind <- sample(seq_len(nrow(data)), size = smp_size)
  
  return(train_ind)
}

aspect_opinion <- read.csv("reviews_to_opinions_clean.csv")
train_ind <- get_portion_of_sample(aspect_opinion, 0.70)

aspect_opinion_train <- aspect_opinion[train_ind, ]
aspect_opinion_valid <- aspect_opinion[-train_ind, ]
# aspect_opinion_valid_test <- aspect_opinion[-train_ind, ]
# 
# valid_ind <- get_portion_of_sample(aspect_opinion_valid_test, 0.50)
# 
# aspect_opinion_valid <- aspect_opinion_valid_test[valid_ind,]
# aspect_opinion_test <- aspect_opinion_valid_test[-valid_ind,]