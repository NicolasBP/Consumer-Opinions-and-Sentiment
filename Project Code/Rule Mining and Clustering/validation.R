require(arules)
require(arulesViz)
library(ggplot2)
source('frequent_itemset_test.R')


model_fit <- function(data, number_of_clusters){
  model_rules_valid <- run_model(data[,c('feature_LEMMA', 'opinion_LEMMA')], number_of_clusters)
  model_rules_valid <- sort(model_rules_valid, decreasing = TRUE, na.last = NA, by = "confidence")
}

predict_opinion <- function(row, rules, items){
  #aspect <- encode(row['cluster_number_feature'], items)
  aspect <- encode(paste("cluster_number_feature=",row['cluster_number_feature'], sep = ""), items)
  # find all rules, where the lhs is a subset of the current aspect
  rulesMatchLHS <- is.subset(rules@lhs,aspect)
  # and the rhs is NOT a subset of the current aspect (so that some items are left as potential recommendation)
  suitableRules <-  rulesMatchLHS & !(is.subset(rules@rhs,aspect))
  
  # here they are
  inspect(rules[suitableRules])
  
  cluster_number_opinion <- tryCatch(
    {
      # now extract the matching rhs ...
      recommendations <- strsplit(LIST(rules[suitableRules]@rhs)[[1]],split=" ")
      recommendations <- lapply(recommendations,function(x){paste(x,collapse=" ")})
      recommendations <- as.character(recommendations)
      
      # ... and remove all items which are already in the aspect group
      #recommendations <- recommendations[!sapply(recommendations,function(x){aspect %in% x})]
      
      return(as.integer(gsub("cluster_number_opinion=","",recommendations)))
    },
    error = function(cond){
      return(0)
    }
  )
  return(cluster_number_opinion)
}

prediction_function <- function(data, model_fit, number_of_clusters){
  labeled_clustered_itemsets <- get_labeled_clustered_itemsets(data[,c('feature_LEMMA', 'opinion_LEMMA')], number_of_clusters)
  items <- unique(labeled_clustered_itemsets[['cluster_number_feature']])
  items <- lapply(items, function(x){paste('cluster_number_feature=', x, sep = '')})
  # items <- apply(items, function(item) paste('{cluster_number_feature=', item, '}', sep = ''))
  #items <- c("cluster_number_feature=1", "cluster_number_feature=2", "cluster_number_feature=3")
  labeled_clustered_itemsets['predicted_opinions'] <- apply(labeled_clustered_itemsets, 1, function(x) predict_opinion(x,model_fit, items))
  return(labeled_clustered_itemsets['predicted_opinions'])
}


calculate_error <- function(yhat, y){
  errors <- as.integer(y[,1])-as.integer(yhat[,1])
  prediction_error <- length(errors[errors != 0])
  total_observations <- length(errors)
  total_prediction_error <- prediction_error/total_observations
  return(total_prediction_error)
}

k_fold_cross_validations = function(data, k = 10, fit.function, prediction.function, performance.function, prediction.var, tuning_params){
  set.seed(1)
  #Randomly shuffle the data
  data<-data[sample(nrow(data)),]
  
  #Create k equally size folds
  folds <- cut(seq(1,nrow(data)),breaks=k,labels=FALSE)
  #Create a list to collect performance accross folds.
  performance = list()
  for(i in 1:k){
    #Segement the data by fold
    testIndexes <- which(folds==i,arr.ind=TRUE)
    testData <- data[testIndexes, ]
    trainData <- data[-testIndexes, ]
    y <- testData[prediction.var]
    model.fit <- fit.function(trainData[,c('feature_LEMMA', 'opinion_LEMMA')], tuning_params)
    yhat <- prediction.function(testData, model.fit, tuning_params)
    if(length(yhat)!=length(y)){
      print('Different Lengths')
    }
    performance[i] <- performance.function(yhat, y)
  }
  average_performance = mean(unlist(performance))
  return(average_performance)
}




# labeled_clustered_itemsets <- get_labeled_clustered_itemsets(aspect_opinion_valid[,c('feature_LEMMA', 'opinion_LEMMA')], 2)
# items <- unique(labeled_clustered_itemsets[['cluster_number_feature']])
# items <- lapply(items, function(x){paste('cluster_number_feature=', x, sep = '')})
# labeled_clustered_itemsets['predicted_opinions'] <- apply(labeled_clustered_itemsets, 1, function(x) predict_opinion(x,model_rules_valid, items))
# 
# errors <- as.integer(labeled_clustered_itemsets[,'cluster_number_opinion']) - as.integer(labeled_clustered_itemsets[,'predicted_opinions'])
# prediction_error <- length(errors[errors != 0])
# total_observations <- length(errors)
# total_prediction_error <- prediction_error/total_observations
aspect_opinion_valid <- aspect_opinion_valid[,c('feature_LEMMA', 'opinion_LEMMA')]
itemsets <- get_frequent_itemsets(aspect_opinion_valid, 0.001)
clusters_fit <- fit_clusters(itemsets)

results <- data.frame("number_of_clusters" = numeric(),"prediction_error" = numeric())

opinion_mining_cluster_kfold <- function(results, data, clusters_fit, min_clusters, max_clusters){
  for (cluster in seq(min_clusters,max_clusters)){
    groups <- find_clusters(clusters_fit, cluster)
    n_clusters <- get_itemsets_in_clusters(itemsets, groups)
    aspect_opinion_valid <- label_observations_with_cluster_numbers(data, n_clusters)
    average_performance <- k_fold_cross_validations(aspect_opinion_valid, 10, model_fit, prediction_function, calculate_error, 'cluster_number_opinion', cluster)
    results <- insertRow(results, c(cluster, average_performance))
  }
  return(results)
}

kfold_results <- opinion_mining_cluster_kfold(results, aspect_opinion_valid, clusters_fit, 1, 15)


dev.off()
jpeg('validation_results.png')
ggplot(data=kfold_results, aes(x=number_of_clusters, y=prediction_error, group=1)) +
  geom_line()+
  geom_point()+
  labs(title="Prediction Error vs Number of Clusters",x="Number of Clusters", y = "Prediction Error")
dev.off()

print(kfold_results)




############# Results From Previous Runs ###################

# validation_prediction_error <- c(0.2850470, 0.4400626, 0.4769485, 0.4943848, 0.5118166, 0.6248412, 0.7678345, 0.8148143, 0.8357047, 0.8108591, 0.8316823, 0.8236376, 0.8491320, 0.8551723, 0.8336689)
# number_of_clusters_validation <- c(1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15)
# validation_results_import <- data.frame(number_of_clusters_validation, validation_prediction_error)

# jpeg('validation_results.jpeg')
  # ggplot(data=validation_results_import, aes(x=number_of_clusters_validation)) +
  #   geom_line(aes(y = validation_prediction_error, colour = "black")) +
  #   labs(title="Error vs Number of Clusters",x="Number of Clusters", y = "Prediction Error")
# dev.off()
# 
# ggplot(data=validation_results_import, aes(x=number_of_clusters_validation)) +
#   geom_line(aes(y = validation_prediction_error, colour = "black")) +
#   labs(title="Error vs Number of Clusters",x="Number of Clusters", y = "Prediction Error")


# validation_prediction_error <- c(0.3630045, 0.4067965, 0.4456899, 0.4801269, 0.5824231, 0.6719491, 0.8559938, 0.8479540, 0.8363629, 0.7867433, 0.7880365, 0.8036795, 0.7902907, 0.8064202, 0.7956478)
# number_of_clusters_validation <- c(1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15)
# validation_results_import <- data.frame(number_of_clusters_validation, validation_prediction_error)
# 
# ggplot(data=validation_results_import, aes(x=number_of_clusters_validation)) +
#   geom_line(aes(y = validation_prediction_error, colour = "black")) +
#   scale_color_manual(labels = c("Prediction Error"), values = c("black")) +
#   labs(title="Error vs Number of Clusters",x="Number of Clusters", y = "Prediction Error")