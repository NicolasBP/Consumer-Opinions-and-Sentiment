import pandas as pd
import json

#json.loads('reviews_Health_and_Personal_Care_5.json')

reviews = []
reviews_health = []

with open('reviews_Grocery_and_Gourmet_Food_5.json') as f:
    for line in f:
        reviews.append(json.loads(line))

with open('reviews_Health_and_Personal_Care_5.json') as f:
    for line in f:
        reviews_health.append(json.loads(line))

reviews_df = pd.DataFrame(reviews)

reviews_health_df = pd.DataFrame(reviews_health)

reviews_df.to_csv('amazon_reviews.csv')

meal_replacement_asin = pd.read_csv('meal_replacement_products_asin.csv')

#Define a list of products to analyze
#products = ['B01EUEIL3E', 'B00NL2COGC', 'B0163J4MJ6', 'B01K8AFNTY', 'B00RWWOKL4', 'B007S6Y74O']

#Filter reviews by product
#product_reviews_df = reviews_df.loc[reviews_df['asin'].isin(products)]

#Extract reviews that are related to meal replacement products
##print 'Before filtering: ', len(reviews_df)
##meal_replacement_products = list(reviews_df[reviews_df['reviewText'].str.contains('meal replacement')].asin)

##print 'After filtering: ', len(meal_replacement_products)
##reviews_df = reviews_df[reviews_df.asin.isin(meal_replacement_products)]
#reviews_df = pd.merge(reviews_df, meal_replacement_products, how='inner', on=['asin'])
reviews_df = pd.merge(reviews_df, meal_replacement_asin, how='inner', on=['asin'])
reviews_health_df = pd.merge(reviews_health_df, meal_replacement_asin, how='inner', on=['asin'])
##print 'After merging: ', len(reviews_df)
reviews_df.to_csv('meal_replacement_product_reviews1.csv')
reviews_health_df.to_csv('meal_replacement_product_reviews2.csv')

meal_replacement_reviews = pd.concat([reviews_health_df, reviews_df], ignore_index = True)
meal_replacement_reviews.to_csv('meal_replacement_product_reviews.csv')

#Load list of product features
####features = pd.read_csv('product-features.csv')
####features_list = features['Feature'].tolist()
##reviews_df.to_csv('amazon_reviews_meal_replacement.csv')
#Find product reviews
#features_reviews = reviews_df.loc[[reviews_df[col].str.contains("gluten") for col in ['reviewText']]]['reviewerID']

def filter_reviews_by_features_list(features_list, reviews_df):
    pattern = '|'.join(features_list)
    features_reviews_df = reviews_df[reviews_df.reviewText.str.contains(pattern)]
    return features_reviews_df

####features_reviews_df = filter_reviews_by_features_list(features_list, reviews_df)

#features_df = pd.DataFrame(columns = features_list)
#reviews_to_features_column_names = list('reviewText').append(features_list)
####features_df  = pd.DataFrame(columns = features_list)

####reviews_to_features = pd.concat([features_reviews_df, features_df], axis = 1)

def filter_reviews_by_feature(col, x):
    index = x.reviewText.find(col)
    x[col] = index
    return x

####reviews_to_features_result = [reviews_to_features.apply(lambda x: filter_reviews_by_feature(col, x), axis = 1) for col in features_list]
####reviews_to_features_result.to_csv('reviews_to_features_result.csv')