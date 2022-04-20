import requests
import json

### Below is the test code to implement the resaurant API and geocoding API used to collect the lat long from
## the user's sepcified locations

# url = "https://google-maps-geocoding.p.rapidapi.com/geocode/json"
# querystring = {"address":"1330 Ethel Street, Kelowna BC","language":"en"}
# headers = {
# 'x-rapidapi-host': "google-maps-geocoding.p.rapidapi.com",
# 'x-rapidapi-key': "90a274727dmsh607a63ae7dd7473p12f953jsn5e3fb6071646"
# }
# response = requests.request("GET", url, headers=headers, params=querystring)
# data = json.loads(response.text)
# lat = data['results'][0]['geometry']['location']['lat']
# long = data['results'][0]['geometry']['location']['lng']
# print('long is {} lat is {}'.format(long, lat))

# url = "https://travel-advisor.p.rapidapi.com/restaurants/list-by-latlng"

# querystring = {"latitude":lat,"longitude":long,"limit":"5","currency":"CAD","combined_food":"French","distance":"2","open_now":"true","lunit":"km","lang":"en_US","min_rating":"3"}

# headers = {
# 	"X-RapidAPI-Host": "travel-advisor.p.rapidapi.com",
# 	"X-RapidAPI-Key": "90a274727dmsh607a63ae7dd7473p12f953jsn5e3fb6071646"
# }

# response = requests.request("GET", url, headers=headers, params=querystring).json()

# # string_builder = ''
# # for list_results in response['data']:
# #     name = list_results['name']
# #     print(name)

# for lr in response['data']:
#     # print(lr)
#     if 'name' in lr:
#         print(lr['name']+"\n"+lr['address']+"\n"+lr['web_url']+"\n")



###############
# Directions API
################
ad1 = "1330 Ethel Street, Kelowna BC"
ad2 = "852 Stockwell Ave, Kelowna BC"

addresses = [ad1, ad2]
coords = []
for e in addresses:
	url1 = "https://google-maps-geocoding.p.rapidapi.com/geocode/json"
	querystring = {"address":e,"language":"en"}
	headers = {
	'x-rapidapi-host': "google-maps-geocoding.p.rapidapi.com",
	'x-rapidapi-key': "90a274727dmsh607a63ae7dd7473p12f953jsn5e3fb6071646"
	}
	response = requests.request("GET", url1, headers=headers, params=querystring)
	data = json.loads(response.text)
	lat = data['results'][0]['geometry']['location']['lat']
	long = data['results'][0]['geometry']['location']['lng']
	coords.append(lat)
	coords.append(long)

corString = str(coords[0])+","+str(coords[1])+"|"+str(coords[2])+","+str(coords[3])

url = "https://route-and-directions.p.rapidapi.com/v1/routing"

querystring = {"waypoints":corString,"mode":"drive"}

headers = {
	"X-RapidAPI-Host": "route-and-directions.p.rapidapi.com",
	"X-RapidAPI-Key": "90a274727dmsh607a63ae7dd7473p12f953jsn5e3fb6071646"
}

response = requests.request("GET", url, headers=headers, params=querystring).json()

for el in range(0, len(response['features'][0]['properties']['legs'][0]['steps'])):
    pair = response['features'][0]['properties']['legs'][0]['steps'][el]['instruction']
    print(pair['text'])