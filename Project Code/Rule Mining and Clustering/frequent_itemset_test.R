require(arules)
require(arulesViz)
require(boot)
source('data.R')
#aspect_opinion <- read.csv("reviews_to_opinions_clean.csv")
aspect_opinion_train <- aspect_opinion_train[,c('feature_LEMMA', 'opinion_LEMMA')]
#aspect_opinion <- as.data.frame(aspect_opinion)
#rules <- apriori(aspect_opinion, parameter = list(supp = 0.01, minlen = 2, target = "frequent itemsets"))



get_frequent_itemsets <- function(data, support){
  itemsets <- apriori(data, parameter = list(supp = support, minlen = 2, target = "frequent itemsets"))
  return(itemsets)
}

fit_clusters <- function(itemsets){
  fit <- hclust(dissimilarity(itemsets), method="ward")
  return(fit)
}

find_clusters <- function(fit, number_of_clusters){
  groups <- cutree(fit, number_of_clusters)
  return(groups)
}

plot_clusters <- function(fit, number_of_clusters){
  plot.new()
  plot(fit) # display dendogram
  rect.hclust(fit, k=number_of_clusters, border="red")
}

get_cluster_itemsets <- function(cluster_number, clusters){
  return(inspect(rules[groups.10==10]))
}

get_itemsets_in_clusters <- function(itemsets, groups){
  item_sets <- as.data.frame(inspect(itemsets))
  item_sets['cluster_number'] <- NA
  item_sets['cluster_number'] <- groups
  if(nrow(item_sets) != length(groups)){
    print('Error')
  }
  return(item_sets)
}

label_observations_with_cluster_numbers <- function(data, labeled_clustered_itemsets){
  data[,'cluster_number_set'] <- NA
  data[,'cluster_number_feature'] <- NA
  data[,'cluster_number_opinion'] <- NA
  
  labeled_clustered_itemsets$items <- lapply(labeled_clustered_itemsets$items, as.character)
  
  check_partial_cluster_belonging <- function(row, feature_or_opinion){
    cluster_numbers <- NULL
    # get_mode <- function(x) {
    #   ux <- unique(x)
    #   ux[which.max(tabulate(match(x, ux)))]
    # }
    # cluster_numbers <- labeled_clustered_itemsets$cluster_number[grepl(paste(feature_or_opinion,'=',row[feature_or_opinion], sep = ""), labeled_clustered_itemsets$items)]
    clusters_containing_aspect_opinion <- labeled_clustered_itemsets[grepl(paste(feature_or_opinion,'=',row[feature_or_opinion], sep = ""), labeled_clustered_itemsets$items),]
    cluster_numbers <- unique(clusters_containing_aspect_opinion[,'cluster_number'])
    
    if(length(cluster_numbers)==0){
      return(0)
    }
    
    cluster_number <- 0
    highest_support <- 0
    for(i in cluster_numbers){
      total_support <- 0
      total_support <- sum(clusters_containing_aspect_opinion$support[clusters_containing_aspect_opinion['cluster_number']==i])
      if(total_support > highest_support){
        highest_support <- total_support
        cluster_number <- i
      }
    }
    return(cluster_number)
    # if(length(cluster_numbers)==0){
    #   cluster_numbers <-c(0)
    # }
    
    # return(get_mode(cluster_numbers))
  }
  
  find_cluster_numbers <- function(row){
    cluster_number_set <- labeled_clustered_itemsets$cluster_number[labeled_clustered_itemsets$items == paste('{feature_LEMMA=',row['feature_LEMMA'],',opinion_LEMMA=',row['opinion_LEMMA'],'}', sep = "")]
    row['cluster_number_set'] <- NA
    if(length(cluster_number_set)==0){
      row['cluster_number_set'] <- 0
    }else{
      row['cluster_number_set'] <- cluster_number_set  
    }
    return(row['cluster_number_set'])
  }
  
  find_cluster_numbers_features <- function(row){
    cluster_number_feature <- check_partial_cluster_belonging(row, 'feature_LEMMA')
    row['cluster_number_feature'] <- NA
    row['cluster_number_feature'] <- cluster_number_feature
    return(row['cluster_number_feature'])
  }
  
  find_cluster_numbers_opinions <- function(row){
    cluster_number_opinion <- check_partial_cluster_belonging(row, 'opinion_LEMMA')
    row['cluster_number_opinion'] <- NA
    row['cluster_number_opinion'] <- cluster_number_opinion
    return(row['cluster_number_opinion'])
  }
  
  
  
  data <- as.data.frame(data)
  data$cluster_number_set <- apply(data, 1, function(x) find_cluster_numbers(x))
  data$cluster_number_feature <- apply(data, 1, function(x) find_cluster_numbers_features(x))
  data$cluster_number_opinion <- apply(data, 1, function(x) find_cluster_numbers_opinions(x))
  #data$cluster_number_set[is.na(data$cluster_number_set)] <- data$cluster_number_feature[is.na(data$cluster_number_set)]
  #data$cluster_number_set[is.na(data$cluster_number_set)] <- data$cluster_number_opinion[is.na(data$cluster_number_set)]
  return(data)
}

get_labeled_clustered_itemsets <- function(aspect_opinion, number_of_clusters){
  itemsets <- get_frequent_itemsets(aspect_opinion, 0.001)
  clusters <- fit_clusters(itemsets)
  groups <- find_clusters(clusters, number_of_clusters)
  n_clusters <- get_itemsets_in_clusters(itemsets, groups)
  aspect_opinion <- label_observations_with_cluster_numbers(aspect_opinion, n_clusters)
  #aspect_opinion <- aspect_opinion[,1:3]
  aspect_opinion <- aspect_opinion[,4:5]
  return(aspect_opinion)
}

boot.fun <- function(number_of_clusters, aspect_opinion, indices){
  boot_result <- tryCatch({
    #aspect_opinion = aspect_opinion[index]
    aspect_opinion <- aspect_opinion[indices,]
    itemsets <- get_frequent_itemsets(aspect_opinion, 0.001)
    clusters <- fit_clusters(itemsets)
    groups <- find_clusters(clusters, number_of_clusters)
    n_clusters <- get_itemsets_in_clusters(itemsets, groups)
    aspect_opinion <- label_observations_with_cluster_numbers(aspect_opinion, n_clusters)
    #aspect_opinion <- aspect_opinion[,1:3]
    aspect_opinion <- aspect_opinion[,4:5]
    #aspect_opinion$cluster_number_set <- as.factor(aspect_opinion$cluster_number_set)
    aspect_opinion$cluster_number_feature <- as.factor(aspect_opinion$cluster_number_feature)
    aspect_opinion$cluster_number_opinion <- as.factor(aspect_opinion$cluster_number_opinion)
    itemsets2 <- get_frequent_itemsets(aspect_opinion, 0.001)
    if(number_of_clusters==10){
      print(number_of_clusters)
    }
    rules <- apriori(aspect_opinion, parameter = list(supp = 0.001, conf= 0.001, minlen = 2, target = "rules"))
    inspect_rules <- inspect(rules)
    lift <- inspect_rules[,'lift']
    mean_lift <- mean(lift)
    support <- inspect_rules[,'support']
    mean_support <- mean(support)
    confidence <- inspect_rules[,'confidence']
    mean_confidence <- mean(confidence)
    return(c(mean_support, mean_confidence, mean_lift))
  },
  error = function(cond){
    print(paste('Error finding', number_of_clusters, ' clusters on bootstrap sample', sep = " "))
    print(cond)
    return(c(NA, NA, NA))
  }
  )
  return(boot_result)
}

do_bootsrap <- function(aspect_opinion, boot.fun, R, clusters){
  set.seed(1)
  results <- boot(data=aspect_opinion, statistic=boot.fun, R=R, number_of_clusters=clusters)
  print(paste('Number of errors:', sum(is.na(results$t[,1])), 'out of', R, sep = " "))
  return(c(mean(results$t[,1][!is.na(results$t[,1])]), mean(results$t[,2][!is.na(results$t[,1])]), mean(results$t[,3][!is.na(results$t[,1])])))
}

insertRow <- function(existingDF, newrow) {
  existingDF[nrow(existingDF)+1,] <- newrow
  existingDF
}


opinion_mining_cluster_resampling <- function(results, aspect_opinion, min_clusters, max_clusters){
  #colnames(results)<- c("mean_support","mean_confidence","mean_lift", "number_of_clusters")
  for (cluster in seq(min_clusters,max_clusters)){
    print(paste('Number of clusters', cluster))
    results <- insertRow(results, c(do_bootsrap(aspect_opinion, boot.fun, 500, cluster),c(cluster)))
    print('Results so far:')
    print(results)
  }
  return(results)
}

run_model <- function(aspect_opinion, number_of_clusters){
  itemsets <- get_frequent_itemsets(aspect_opinion, 0.001)
  clusters <- fit_clusters(itemsets)
  groups <- find_clusters(clusters, number_of_clusters)
  n_clusters <- get_itemsets_in_clusters(itemsets, groups)
  aspect_opinion <- label_observations_with_cluster_numbers(aspect_opinion, n_clusters)
  #aspect_opinion <- aspect_opinion[,1:3]
  aspect_opinion <- aspect_opinion[,4:5]
  #aspect_opinion$cluster_number_set <- as.factor(aspect_opinion$cluster_number_set)
  aspect_opinion$cluster_number_feature <- as.factor(aspect_opinion$cluster_number_feature)
  aspect_opinion$cluster_number_opinion <- as.factor(aspect_opinion$cluster_number_opinion)
  itemsets2 <- get_frequent_itemsets(aspect_opinion, 0.001)
  rules <- apriori(aspect_opinion, parameter = list(supp = 0.001, conf= 0.001, minlen = 2, target = "rules"))
  #plot(rules,method="graph",interactive=TRUE,shading=NA)
  return(rules)
}


# aspect_opinion <- aspect_opinion[,c('feature_LEMMA', 'opinion_LEMMA')]
# inspect(sort(apriori(aspect_opinion, parameter = list(supp = 0.001, conf= 0.001, minlen = 2, target = "rules")), by="support"))
# results <- data.frame("mean_support" = numeric(),"mean_confidence" = numeric(),"mean_lift" = numeric(), "number_of_clusters" = numeric())
# boot_results <- opinion_mining_cluster_resampling(results, aspect_opinion_train, 2, 3)



#boot_results <- opinion_mining_cluster_resampling(aspect_opinion_train, 1, 15)


#plot(boot_results[,c('number_of_clusters', 'mean_lift')])
#plot(boot_results[,c('number_of_clusters', 'mean_support')])
#plot(boot_results[,c('number_of_clusters', 'mean_confidence')])



# model_rules <- run_model(aspect_opinion, 2)
# plot(model_rules,method="graph",interactive=TRUE,shading=NA)
# inspect(model_rules)