from flask import Flask, render_template, request, url_for          
import json
restaurants = []
with open('static/json_files/restaurants.json', 'r') as fp:
    restaurants = json.load(fp)
# print(restaurants)

suggested_filters = ['Open Now','Offers Delivery','Offers Takeout','Good for Dinner','Outdoor Seating', 'Good for Lunch']
category_filters = ['Mexican','Tex-Mex','Tacos','Latin American','Restaurants','Bars']
features_filters =['Good for Kids','Good for Groups','Dogs Allowed','Full Bar','Good for Brunch']
distance_filters = ['Bird\'s-eye view','Driving (5mi.)','Walking (5mi.)','Within 4 blocks']
current_location = 'Lakeland, FL'

app = Flask(__name__)

@app.route('/')
def index():
    return "a Yelp clone for CS612"

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/restaurants')
def restaurants_list():
    return render_template('restaurants.html',
                           restaurants = restaurants,
                           suggested_filters = suggested_filters,
                           category_filters = category_filters,
                           features_filters = features_filters,
                           distance_filters = distance_filters,
                           current_location = current_location
                           

                           )
@app.route('/single_restaurant/<restaurant_name>')
def single_restaurant(restaurant_name):
    restaurant_data = {'name': 'Could not find that restaurant.'}

    for restaurant in restaurants:
        if restaurant['name'] == restaurant_name:
            restaurant_data = restaurant
    print(restaurant_data)
    return render_template('single_restaurant.html', 
                           restaurant_data = restaurant_data
                           )



@app.route('/about')
def about():
    return "<h1> About page</h1>"

if __name__ == "__main__":
    app.run(debug = True)