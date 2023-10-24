from flask import Flask, render_template, request, url_for ,jsonify         
import json
import time,datetime
import sqlite3 
from pymongo import MongoClient, InsertOne
from pprint import pprint
from collections import namedtuple

from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map




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




# sql database connection 

import os

basedir = os.path.abspath(os.path.dirname(__file__))
db_file_name = 'static/database/yelp_academic_dataset.db'


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

def get_hour_map(str_json):
    if not str_json:
        return {}
    str_json = str_json[1:-1].replace("'","")
    
    day_time = {}
    for item in str_json.split(","):
        temp =  item.split(": ")
        day,time = temp[0],temp[1]
        day_time.update({day:time})
        pprint(day_time)
    return day_time

    
#==================================



app = Flask(__name__)



@app.route('/')
def index():
    return "a Yelp clone for CS612"

@app.route('/home')
def home():
    return render_template('home.html')



@app.route('/search')
def restaurants_list():
    pageno = request.args.get("pageno","1") 
    pageno = int(pageno)
    description = request.args.get("find_desc","restaurant") 
    location = request.args.get("find_loc","wilmington")
    location_search_string = f" and  ( b.address like '%{location}%' \
        or b.city  like '%{location}%' \
        or b.state  like '%{location}%' \
    )"

    desc_search_string = f" and  ( b.categories like '%{description}%')"
    
   
    str_query = f"SELECT r.id, r.name , r.alias, r.display_phone, r.price,"
    str_query += f"b.address,b.city,b.state,b.stars, b.categories , r.review_count, r.image_url,"
    str_query += f" b.hours, r.coordinates "
    str_query += f" FROM business b, restaurant r"
    str_query += f" where b.business_id = r.id "
    str_query += f" and ( b.categories like '%restaurant%' or b.categories like '%food%') "
    str_query += f" { location_search_string } "
    str_query += f" {desc_search_string} "
    str_query += f" LIMIT 40   "
    print(str_query)
    conn = connect_db(db_file_name)
    restaurant_data = conn.cursor().execute(str_query).fetchall()
    conn.close()
    page_count = round(len(restaurant_data)/10)
    restaurants = restaurant_data[10*pageno-9:10*pageno]
    locations = []
    for restaurant in restaurants:
        coordinate = json.loads(restaurant[13].replace("\'","\""))
        name = restaurant[1]
        locations.append([name,coordinate['latitude'],coordinate['longitude']])
    print(locations)
    
    # str_query = "SELECT text from review\
    #             where business_id = 'Dy91wdWkwtI_qgjAIZ0Niw'\
    #             order by useful desc\
    #             LIMIT 1"
    # review= connect_db(db_file_name).cursor().execute(str_query).fetchone()[0]
    
    
    return render_template('restaurants.html',
                           restaurants = restaurants,
                           pageno=pageno,
                           page_count = page_count,
                           locations = locations
                        #    review = review
                        #    review_data = review_data,
                        #    suggested_filters = suggested_filters,
                        #    category_filters = category_filters,
                        #    features_filters = features_filters,
                        #    distance_filters = distance_filters,
                        #    current_location = current_location
                           

                           )



@app.route('/restaurant')
def restaurant():
    # business_id = "MTSW4McQd7CbVtyjqoe9mw"
    business_id = request.args.get("business_id")
    city = request.args.get("city")
    filter_type = int(request.args.get("filter_type",0))
    sort_type = request.args.get("sort_type",None)
    search_string = request.args.get("word","")
    # print(business_id,filter_type)
    str_query = f" SELECT r.id, r.name , r.alias, r.display_phone, r.price,\
        b.address,b.city,b.state,b.stars, b.categories , r.review_count, r.image_url,\
        b.hours, b.postal_code \
        FROM business b, restaurant r \
        where b.business_id = r.id \
        and b.business_id = '{business_id}'"
    list_of_keys = "business_id name alias display_phone price address city state stars categories review_count image_url hours".split(" ")
    print(str_query)
    conn = connect_db(db_file_name)
    query_result = conn.cursor().execute(str_query).fetchone()
    conn.close()
    restaurant_data =  dict(zip(list_of_keys,query_result))
    restaurant_data['hours'] = get_hour_map(restaurant_data['hours'])
    

    # == 
    sort_string = "order by useful desc"
    if sort_type:
        if sort_type == "newestfirst":
            sort_string = "order by date desc"
        elif sort_type == "oldestfirst":
            sort_string = "order by date asc"
        elif sort_type == "highestrated":
            sort_string = "order by stars desc"
        elif sort_type == "lowestrated":
            sort_string = "order by stars asc"
        elif sort_type == "elites":
            sort_string = "order by useful desc"
    else:
        sort_string = "order by useful desc"

    filter_dict = {
        5:"and stars = 5.0",
        4:"and stars = 4.0",
        3:"and stars = 3.0",
        2:"and stars = 2.0",
        1:"and stars = 1.0",
        0:""

    }
    filter_string  = filter_dict[filter_type]
    review_search_string = f"and text like '%{search_string}%'"
    str_query = f"SELECT name ,business_id, stars , useful, funny, cool,date,text from review_table\
                where business_id = '{business_id}' \
                {review_search_string} \
                {filter_string} \
                {sort_string}\
                LIMIT 10"
    print(str_query)
    conn = connect_db(db_file_name)
    reviews = conn.cursor().execute(str_query).fetchall()
    conn.close()

    # return "<h1>"+str(restaurant_data['hours'])+"</h1>"
    
    
    
    # reviews = col_review.find({"business_id": business_id })

    
    # if sort_type:
    #     if sort_type == "newestfirst":
    #         reviews= reviews.sort('date',-1)
    #     elif sort_type == "oldestfirst":
    #         reviews= reviews.sort('date',1)
    #     elif sort_type == "highestrated":
    #         reviews= reviews.sort('stars',1)
    #     elif sort_type == "lowestestrated":
    #         reviews= reviews.sort('stars',-1)
    #     elif sort_type == "elites":
    #         reviews= reviews.sort('usefule',1)



    # review_data =[]
    
     
    # for review in reviews:
    #     count_stars[str(int(review['stars']))] += 1
    #     user_id = review['user_id']
        
    #     review['name'] =  reviewer_names[user_id]
    #     review_data.append(review)



    
    return render_template('single_restaurant.html', 
                           restaurant_data = restaurant_data,
                           reviews = reviews,
                           search_string = search_string

                           
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



@app.context_processor
def get_reviews_of_a_business():
    def get_one_review(business_id):
        str_query = f"SELECT name ,business_id, stars , useful, funny, cool,date,text from review_table\
                    where business_id = '{business_id}' \
                    LIMIT 1" 
        conn = connect_db(db_file_name)   
        reviews = conn.cursor().execute(str_query).fetchall()
        conn.close()
        review_comment = reviews[0][7]
        return f"{review_comment[:80]}"
    

    return dict(get_one_review=get_one_review)

@app.context_processor
def get_reviews_percent_of_a_business():
    def get_review_percent(business_id):
        import numpy as np
        str_query = f"select stars ,count(stars) from review_table \
            where business_id = '{business_id}' \
            group by stars"
        conn  = connect_db(db_file_name)
        rows = conn.cursor().execute(str_query).fetchall()
        print(f"getting review percent for {business_id}")
        conn.close()
        sum = np.sum([row[1] for row in rows])
        
        review_percent = [0,0,0,0,0]
        if not sum == 0:
              
            for row in rows:
                print(row)
                review_percent[int(row[0])-1] = int(100*row[1]/sum)
            
        print(review_percent)
        return review_percent
    return dict(get_review_percent=get_review_percent)


@app.route('/about')
def about():
    return "<h1> About page</h1>"

if __name__ == "__main__":
    # app.run(host='0.0.0.0',port=5000)
    app.run(debug=True)