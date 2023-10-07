from flask import Flask, render_template, request, url_for          
import json
import time,datetime
import sqlite3 
from pymongo import MongoClient, InsertOne
from pprint import pprint


#==============================================
# Mongodb variables

client = MongoClient('localhost', 27017)

# Name of the database
db = client["yelp"]

# Name of the collection
col_business = db["business"]
col_review = db["review"]
col_user = db["user"]

# reviewer_names={}
# reviewer_cols=col_user.find({},{'name':1,'user_id':1,'_id':0})
# for reviewer in reviewer_cols:
#     reviewer_names.update({reviewer['user_id']:reviewer['name']})
#=============================================


restaurants = []

# sql database connection 
basename = 'reviewusers_mini'

db_file_name = basename + '.db'

##
with open('static/json_files/restaurants.json', 'r') as fp:
    restaurants = json.load(fp)
# print(restaurants)

suggested_filters = ['Open Now','Offers Delivery','Offers Takeout','Good for Dinner','Outdoor Seating', 'Good for Lunch']
category_filters = ['Mexican','Tex-Mex','Tacos','Latin American','Restaurants','Bars']
features_filters =['Good for Kids','Good for Groups','Dogs Allowed','Full Bar','Good for Brunch']
distance_filters = ['Bird\'s-eye view','Driving (5mi.)','Walking (5mi.)','Within 4 blocks']
current_location = 'Philadelphia, PA'


#===================================
def connect_db(db_file_name):
    return sqlite3.connect(db_file_name)

def get_current_location():
    from geopy.geocoders import Nominatim
    
#==================================



app = Flask(__name__)

@app.route('/')
def index():
    return "a Yelp clone for CS612"

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/restaurants')
def restaurants_list():
    item = request.args.get("item") 
    city = request.args.get("city")
   
    filter = "open now"
    
    search_dict = {}
    if city :        
        search_dict.update({'city':city})
    else:
        city,state = current_location.split()
        city = city.strip()
        state = state.replace(" ","")
        print(city,state)


            

       
    review_data = []
    count = 0
    print(f"search dict: {search_dict}")
    businesses = col_business.find(search_dict)

    



    for business in businesses:
        temp_dict = business        
        
        reviews = col_review.find_one({"business_id": business['business_id'] })
        temp_dict["first_review"] = reviews['text']
        review_data.append(temp_dict) 
        # print(review_data)    
        
        count += 1
        if count>10: break
     
    return render_template('restaurants.html',
                           restaurants = review_data,
                           review_data = review_data,
                           suggested_filters = suggested_filters,
                           category_filters = category_filters,
                           features_filters = features_filters,
                           distance_filters = distance_filters,
                           current_location = current_location
                           

                           )



@app.route('/restaurant')
def restaurant():
    # business_id = "MTSW4McQd7CbVtyjqoe9mw"
    business_id = request.args.get("business_id")
    city = request.args.get("city")
    filter_type = int(request.args.get("filter_type",0))
    sort_type = request.args.get("sort_type",None)
    print(business_id,filter_type)
    search_dict={}
    search_dict.update({'business_id':business_id})
    if city:search_dict.update({'city':city})
    


    print(f"search string: {search_dict}")
    a_business = col_business.find_one(search_dict)
    print(f"---query complete.")

    # return "<h1>"+str(temp_dict)+"</h1>"
    
    
    
    # reviews = col_review.find({"business_id": business_id })

    
    if sort_type:
        if sort_type == "newestfirst":
            reviews= reviews.sort('date',-1)
        elif sort_type == "oldestfirst":
            reviews= reviews.sort('date',1)
        elif sort_type == "highestrated":
            reviews= reviews.sort('stars',1)
        elif sort_type == "lowestestrated":
            reviews= reviews.sort('stars',-1)
        elif sort_type == "elites":
            reviews= reviews.sort('usefule',1)

    count_stars = {
        '5':0,
        '4':0,
        '3':0,
        '2':0,
        '1':0
    }
    count_stars_percent = {
        '5':25,
        '4':35,
        '3':15,
        '2':20,
        '1':5
    }
    # review_data =[]
    
     
    # for review in reviews:
    #     count_stars[str(int(review['stars']))] += 1
    #     user_id = review['user_id']
        
    #     review['name'] =  reviewer_names[user_id]
    #     review_data.append(review)

    # count_sum = sum([count_stars[key] for key in count_stars.keys()])
    # if count_sum == 0:
    #     count_sum = 1
    # count_stars_percent = { key:int(100*val/count_sum) for (key,val) in count_stars.items() }
    # print(count_stars_percent, count_sum)
    count_sum = 100

    
    return render_template('single_restaurant.html', 
                           restaurant_data = a_business,
                        #    reviews = reviews,
                           count_sum = count_sum,
                           count_stars_percent = count_stars_percent,
                           
                           )
    



    return f"restaurant {business_id}"
@app.route('/single_restaurant/<business_id>')
def single_restaurant(business_id):
    restaurant_data = {'name': 'Could not find that restaurant.'}

    a_business = col_business.find_one({"business_id": business_id})
    # pprint(a_business['name'])


    temp_dict  = {
    "name": a_business['name'],
    "is_open": a_business['is_open'],
    "webpage": "http://www.google.com",
    "phone": "(987) 654-3210",
    "claimed": "True",
    "tags":  a_business["categories"].split(","),
    "hours": a_business["hours"],
    "address": a_business["address"],
    "city": a_business["city"],
    "state": a_business["state"],
    "zip"  : a_business["postal_code"],
    "reviews":[
        {"reviewer":"Tom Cruze","rating":5,"review_comment": ""},
        {"reviewer":"Tom Hardy","rating":1,"review_comment":"Worst Taco place."},
        {"reviewer":"Tom Hanks","rating":3,"review_comment":"Good Taco place."},
        {"reviewer":"Tom Latham","rating":2,"review_comment":"Bad Taco place."}

    ],
    "review_count" : str(a_business["review_count"]),
    "rating": str(a_business["stars"]),
    "int_rating": int(a_business["stars"]),
    "image":"https://s3-media0.fl.yelpcdn.com/bphoto/xOLVZHetASCsUU2VRyi2rA/o.jpg"

    }
    restaurant_data = temp_dict
    reviews = col_review.find({"business_id": business_id })

    

    return render_template('single_restaurant.html', 
                           restaurant_data = restaurant_data,
                           reviews = reviews
                           )


@app.context_processor
def inject_today_date():
    return {'weekday': time.strftime('%A'),'today': datetime.date.today()}


@app.route('/about')
def about():
    return "<h1> About page</h1>"

if __name__ == "__main__":
    # app.run(host='0.0.0.0',port=5000)
    app.run(debug=True)