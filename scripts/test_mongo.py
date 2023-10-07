import pymongo
import json
from pymongo import MongoClient, InsertOne
from pprint import pprint

client = pymongo.MongoClient('localhost', 27017)
 
# Name of the database
database = client["yelp"]

 
# Name of the collection
col_business = database["business"]
col_review = database["review"]
col_user = database["user"]

#  find all businesses
def find_all_businesses ():
    for business in col_business.find():
        temp_dict = business
        business_id = temp_dict['business_id']    
        reviews = col_review.find({"business_id": business_id })
        
        pprint(business)
        print("======================")
        print(next(reviews)['text'])
        break

def find_a_business(business_id):
    business = col_business.find_one({"business_id": business_id})
    pprint(business)

def find_reviews_for_a_business(business_id):
    reviews = col_review.find({"business_id": business_id })
    for review in reviews:
        print(review)

def get_all_stars(business_id, star):
    reviews = col_review.find({"business_id": business_id,"stars": star })
    for review in reviews:
        print(review)


def find_reviews_for_a_business_sorted_by_date(business_id):
    reviews = col_review.find({"business_id": business_id })
    reviews= reviews.sort('date',1)
    for review in reviews:
        print(review)

def find_name_from_user_id(user_id):
    doc = col_user.find({"user_id": user_id },{"user_id":1,"name":1})
    doc = next(doc)
    print(doc)
    return doc["name"]


# find_name_from_user_id("-6GY04bTPM2Zo4z0GN4a1A")

# find_all_businesses()
# find_a_business("MTSW4McQd7CbVtyjqoe9mw")
# find_reviews_for_a_business("MTSW4McQd7CbVtyjqoe9mw")
# get_all_stars("MTSW4McQd7CbVtyjqoe9mw",4.0)
# find_reviews_for_a_business_sorted_by_date("MTSW4McQd7CbVtyjqoe9mw")

'''
mongodb commands:
================
show dbs
use yelp
show collections
'''


'''
SELECT review.text, review.user_id,review.business_id 
FROM review
WHERE review.business_id = "MTSW4McQd7CbVtyjqoe9mw"


https://artemiorimando.com/2017/03/25/yelp-python-json-sql/
https://medium.com/analytics-vidhya/analyzing-yelp-dataset-with-sql-147157a4caed
https://www.youtube.com/watch?v=D5l5Gf7PoJA&list=PLXmMXHVSvS-Db9KK1LA7lifcyZm4c-rwj&index=6&ab_channel=PrettyPrinted
'''