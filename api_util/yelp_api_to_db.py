import requests
# from yelpapi import YelpAPI
import pprint 

url = "https://api.yelp.com/v3/businesses/search"
key = 'r4ZgN8lr0JITPk0hDp1lcXidGGrukWvB8xsDLzD2j9jQhk40OojMmJZxZb7JurIkxec1opGSOw_97-8lNDZGZo_3APL4lira_Sjp70iuox2SIkubSpMHMO-oUWIUZXYx' #open('api_key.txt').readlines()[0].strip()
headers = {
            "Authorization": f"bearer {key}"
        }
parameters ={
        'term':'restaurant', 
        'location':'auburndale, fl', 
        'sort_by':'rating', 
        'limit':2,
        'radius' : 40000
}
response = requests.get(url, headers=headers,params=parameters)

pprint.pprint(response.json())
