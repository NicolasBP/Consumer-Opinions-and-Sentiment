require(ggplot2)
source('frequent_itemset_test.R')

aspect_opinion_train <- aspect_opinion_train[,c('feature_LEMMA', 'opinion_LEMMA')]
results <- data.frame("mean_support" = numeric(),"mean_confidence" = numeric(),"mean_lift" = numeric(), "number_of_clusters" = numeric())
boot_results <- opinion_mining_cluster_resampling(results, aspect_opinion_train, 14, 15)

print(boot_results)

dev.off()
jpeg('confidence_support_train.jpeg')
ggplot(data=boot_results, aes(x=number_of_clusters)) +
  geom_line(aes(y = mean_support, colour = "blue")) + 
  geom_line(aes(y = mean_confidence, colour = "red")) + 
  labs(title="Confidence and Support vs Number of Clusters",x="Number of Clusters", y = "Prediction Error")
dev.off()

jpeg('lift_training.jpeg')
ggplot(data=boot_results, aes(x=number_of_clusters)) +
  geom_line(aes(y = mean_lift, colour = "black")) + 
  labs(title="Lift vs Number of Clusters",x="Number of Clusters", y = "Prediction Error")
dev.off()


############# Results From Previous Runs ###################

# mean_support_boot <- c(0.250000000, 0.112715083, 0.067412387, 0.046020148, 0.033954087, 0.026324243, 0.021265392, 0.017635024, 0.015037010, 0.013108414, 0.011611493, 0.010437766, 0.009538518, 0.008792546, 0.008173027)
# mean_confidence_boot <- c(0.5000000, 0.3377722, 0.2683787, 0.2277904, 0.2003987, 0.1802805, 0.1656009, 0.1538145, 0.1451031, 0.1385201, 0.1332816, 0.1292525, 0.1265924, 0.1245156, 0.1228781)
# mean_lift_boot <- c(1.060295, 1.378977, 1.468804, 1.479326, 1.481384, 1.489765, 1.519902, 1.558793, 1.632949, 1.724824, 1.824450, 1.918166, 2.028298, 2.137959, 2.254966)
# number_of_clusters_boot <- c(1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15)
# boot_results_import <- data.frame(number_of_clusters_boot, mean_support_boot, mean_confidence_boot, mean_lift_boot)
# 
# jpeg('lift_training.jpeg')
# ggplot(data=boot_results_import, aes(x=number_of_clusters_boot)) +
#   geom_line(aes(y = mean_lift_boot, colour = "black")) +
#   labs(title="Lift vs Number of Clusters",x="Number of Clusters", y = "Lift")
# dev.off()
# 
# ggplot(data=boot_results_import, aes(x=number_of_clusters_boot)) +
#   geom_line(aes(y = mean_support_boot, colour = "black")) +
#   geom_line(aes(y = mean_confidence_boot, colour = "black")) +
#   labs(title="Support/Confidence vs Number of Clusters",x="Number of Clusters", y = "Support/Confidence")






# mean_support_boot <- c(0.25000000, 0.12451577, 0.07237307, 0.04741868, 0.03345156, 0.02492308, 0.01971486, 0.01615927, 0.01373560, 0.01198511, 0.01068548, 0.009697174, 0.008931312, 0.008361053, 0.007914605)
# mean_confidence_boot <- c(0.5000000, 0.3541770, 0.2739761, 0.2253190, 0.1918758, 0.1680886, 0.1519260, 0.1397300, 0.1313978, 0.1255193, 0.1214598, 0.1187120, 0.1169777, 0.1163808, 0.1165015)
# mean_lift_boot <- c(1.044895, 1.256182, 1.369224, 1.366775, 1.340756, 1.346979, 1.369287, 1.421145, 1.513165, 1.622596, 1.738800, 1.860129, 1.989200, 2.134144, 2.304505)
# number_of_clusters_boot <- c(1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15)
# boot_results_import <- data.frame(number_of_clusters_boot, mean_support_boot, mean_confidence_boot, mean_lift_boot)
# 
# ggplot(data=boot_results_import, aes(x=number_of_clusters_boot)) +
#   geom_line(aes(y = mean_support_boot, colour = "blue")) +
#   geom_line(aes(y = mean_confidence_boot, colour = "red")) +
#   scale_color_manual(labels = c("Support", "Confidence"), values = c("blue", "red")) +
#   labs(title="Support/Confidence vs Number of Clusters",x="Number of Clusters", y = "Support/Confidence", colour = "Statistic")
# 
# 
# ggplot(data=boot_results_import, aes(x=number_of_clusters_boot)) +
#   geom_line(aes(y = mean_lift_boot, colour = "black")) +
#   scale_color_manual(labels = c("Lift"), values = c("black")) +
#   labs(title="Lift vs Number of Clusters",x="Number of Clusters", y = "Lift")