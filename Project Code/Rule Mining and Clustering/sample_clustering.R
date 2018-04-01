source('frequent_itemset_test.R')

num_clusters <- seq(1,15,1)

lapply(num_clusters, function(i){
  aspect_opinion <- read.csv("reviews_to_opinions_clean.csv")
  # aspect_opinion['cluster_number_set'] <- NA
  # aspect_opinion['cluster_number_feature'] <- NA
  # aspect_opinion['cluster_number_opinion'] <- NA
  itemsets <- get_frequent_itemsets(aspect_opinion[,c('feature_LEMMA', 'opinion_LEMMA')], 0.001)
  clusters <- fit_clusters(itemsets)
  groups <- find_clusters(clusters, i)
  n_clusters <- get_itemsets_in_clusters(itemsets, groups)
  aspect_opinion_labeled <- label_observations_with_cluster_numbers(aspect_opinion[,c('feature_LEMMA', 'opinion_LEMMA')], n_clusters)
  #clustering_result <- merge(x = aspect_opinion, y = aspect_opinion_labeled, by = c("feature_LEMMA","opinion_LEMMA"))
  #colnames(clustering_result) <- c("good", "better")
  
  aspect_opinion['cluster_number_set'] <- aspect_opinion_labeled['cluster_number_set']
  aspect_opinion['cluster_number_feature'] <- aspect_opinion_labeled['cluster_number_feature']
  aspect_opinion['cluster_number_opinion'] <- aspect_opinion_labeled['cluster_number_opinion']
  write.csv(aspect_opinion, file = paste("aspect_opinion_clusters_", i, ".csv", sep = ""))
})

