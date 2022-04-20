from typing import Any, Text, Dict, List, Union, Optional
import json
from datetime import datetime
import requests



from rasa_sdk import Action, Tracker
from rasa_sdk.types import DomainDict
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    SlotSet,
    AllSlotsReset,
    Restarted
)



class ActionJoke(Action):
    def name(self):
        return "action_tellJoke"
    
    def run(self, dispatcher, tracker, domain):
        request = json.loads(requests.get('https://api.chucknorris.io/jokes/random').text)  # make an api call
        joke = request['value']  # extract a joke from returned json response
        dispatcher.utter_message(joke)  # send the message back to the user
        return []

class ActionSlotReset(Action):
    def name(self) -> Text:
        return 'action_slot_reset'
    
    def run(self, dispatcher, tracker, domain):
        return[AllSlotsReset()]
    

class ActionRestarted(Action):
    def name(self):
        return "action_chat_restart"

    def run(self, dispatcher, tracker, domain):
        return [Restarted()]

class ActionCheckWeather(Action):

    def name(self) -> Text:
        return "action_get_weather"

    def run(self, dispatcher, tracker, domain):
        api_key = '846be7071eb6f82c31610e982ad63cf0'
        loc = tracker.get_slot('weather_location')
        current = requests.get('http://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(loc, api_key)).json()
        #print(current)
        country = current['sys']['country']
        city = current['name']
        condition = current['weather'][0]['main']
        temperature_c = current['main']['temp']
        temperature_c -= 273
        temperature_c = round(temperature_c)
        humidity = current['main']['humidity']
        wind_mph = current['wind']['speed']
        response = """It is currently {} in {} at the moment. The temperature is {} degrees, the humidity is {}% and the wind speed is {} m/s.""".format(condition, city, temperature_c, humidity, wind_mph)
        dispatcher.utter_message(response)
        return [SlotSet('weather_location', loc)]

class ActionSubmitHotelForm(Action):
    
    def name(self) -> Text:
        return "action_hotelForm"
        
    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["hotel_local", "check_in", "number_Adults", "number_rooms", "check_out"]
    

    
    def run(self, dispatcher, tracker, domain):
       
        loc = tracker.get_slot('hotel_local')
        checkI = tracker.get_slot('check_in')
        num_a = tracker.get_slot('number_Adults')
        num_room = tracker.get_slot('number_rooms')
        checkO = tracker.get_slot('check_out')
        
        url1 = "https://google-maps-geocoding.p.rapidapi.com/geocode/json"
        querystring = {"address":loc,"language":"en"}
        headers = {
            'x-rapidapi-host': "google-maps-geocoding.p.rapidapi.com",
            'x-rapidapi-key': "90a274727dmsh607a63ae7dd7473p12f953jsn5e3fb6071646"
            }
        response = requests.request("GET", url1, headers=headers, params=querystring)
        data = json.loads(response.text)
        lat = data['results'][0]['geometry']['location']['lat']
        long = data['results'][0]['geometry']['location']['lng']
        print('long is {} lat is {}'.format(long, lat))
        
        url2 = "https://booking-com.p.rapidapi.com/v1/hotels/search-by-coordinates"
        querystring2 = {"checkin_date":checkI,"order_by":"popularity","units":"metric","longitude":long,"adults_number":num_a,"latitude":lat,"room_number":num_room,"locale":"en-us","filter_by_currency":"USD","checkout_date":checkO,"children_number":"1","children_ages":"5","page_number":"0","categories_filter_ids":"class::2,class::4,free_cancellation::1","include_adjacency":"true"}
        headers = {
                'x-rapidapi-host': "booking-com.p.rapidapi.com",
                'x-rapidapi-key': "90a274727dmsh607a63ae7dd7473p12f953jsn5e3fb6071646"
            }
        response = requests.request("GET", url2, headers=headers, params=querystring2).json()
        string_builder = ''
        for list_result in response['result']:
            hotel_address = list_result['address']
            hotel_id = list_result['hotel_name']
            net_amount = list_result['composite_price_breakdown']['all_inclusive_amount']
            discounted_amount = list_result['composite_price_breakdown']
            string_builder += '<b>' + hotel_id + '</b><br>\n'
            string_builder += '<b>' + hotel_address + '</b><br>\n'
            string_builder += ' ' + str(net_amount['value']) + ' ' + net_amount['currency'] + ' per night<br>\n'
            if 'discounted_amount' in list_result['composite_price_breakdown']:
                string_builder += ' ' +  str(discounted_amount['discounted_amount']['value']) + ' ' + discounted_amount['discounted_amount']['currency'] + ' discount!<br>\n'
            else:
                data['discounted_amount'] = 'No discounts!<br>\n'
                string_builder += ' ' +  'No discounts!<br>\n'
                
            string_builder += ' ' + list_result['distance_to_cc'] + 'km to the city center<br>\n'   
        dispatcher.utter_message(text = string_builder)
        return [SlotSet('hotel_local', loc)]
   
   
class ActionSubmitrestForm(Action):
    
    def name(self) -> Text:
        return "action_rest_form"
        
    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["hotel_local", "hotel_choice", "cuisine", "food_rating", "distance"]
    

    def run(self, dispatcher, tracker, domain):
        loc = tracker.get_slot('hotel_local')
        addr = tracker.get_slot('hotel_choice')
        cuin = tracker.get_slot('cuisine')
        rating = tracker.get_slot('food_rating')
        dist = tracker.get_slot('distance')
        
        addy = str(addr)+", "+str(loc)
        # testr = str(loc)+","+str(addr)+","+str(cuin)+","+str(rating)+","+str(dist)
        
        url = "https://google-maps-geocoding.p.rapidapi.com/geocode/json"
        querystring = {"address":addy,"language":"en"}
        headers = {
        'x-rapidapi-host': "google-maps-geocoding.p.rapidapi.com",
        'x-rapidapi-key': "90a274727dmsh607a63ae7dd7473p12f953jsn5e3fb6071646"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        data = json.loads(response.text)
        lat = data['results'][0]['geometry']['location']['lat']
        long = data['results'][0]['geometry']['location']['lng']
        print('long is {} lat is {}'.format(long, lat))

        url = "https://travel-advisor.p.rapidapi.com/restaurants/list-by-latlng"

        querystring = {"latitude":lat,"longitude":long,"limit":"5","currency":"CAD","combined_food":cuin,"distance":dist,"open_now":"true","lunit":"km","lang":"en_US","min_rating":rating}

        headers = {
            "X-RapidAPI-Host": "travel-advisor.p.rapidapi.com",
            "X-RapidAPI-Key": "90a274727dmsh607a63ae7dd7473p12f953jsn5e3fb6071646"
        }

        response = requests.request("GET", url, headers=headers, params=querystring).json()

        # string_builder = ''
        # for list_results in response['data']:
        #     name = list_results['name']
        #     print(name)
        stringr = ''
        for lr in response['data']:
            if 'name' in lr:
                stringr += lr['name']+"\n"+lr['address']+"\n"+lr['web_url']+"\n"
                
        
        dispatcher.utter_message(text = stringr)      
        return[]
    
class ActionSubmitDirection1Form(Action):
    
    def name(self) -> Text:
        return "action_direction1_form"
        
    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["hotel_local", "hotel_choice", "rest_choice", "mode_transit"]
    

    def run(self, dispatcher, tracker, domain):
        
        loc = tracker.get_slot('hotel_local')
        addr = tracker.get_slot('hotel_choice')
        addy = str(addr)+", "+str(loc)
        ad2 = tracker.get_slot('rest_choice')
        addy2 = str(ad2)+", "+str(loc)
        
        mode = tracker.get_slot('mode_transit')
        
        addresses = [addy, addy2]
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

        querystring = {"waypoints":corString,"mode":mode}

        headers = {
            "X-RapidAPI-Host": "route-and-directions.p.rapidapi.com",
            "X-RapidAPI-Key": "90a274727dmsh607a63ae7dd7473p12f953jsn5e3fb6071646"
        }

        response = requests.request("GET", url, headers=headers, params=querystring).json()
        stri = ''
        for el in range(0, len(response['features'][0]['properties']['legs'][0]['steps'])):
            pair = response['features'][0]['properties']['legs'][0]['steps'][el]['instruction']
            stri+= pair['text']+"\n"
        
        dispatcher.utter_message(text = stri)
        return []
    

class ActionSubmitDirection2Form(Action):
    
    def name(self) -> Text:
        return "action_direction2_form"
        
    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["hotel_local","addy1", "addy2", "mode_transit"]
    

    def run(self, dispatcher, tracker, domain):
        city = str(tracker.get_slot('hotel_local'))
        addy = str(tracker.get_slot('addy1'))+", "+city
        addy2 = str(tracker.get_slot('addy2'))+", "+city
   
        mode = tracker.get_slot('mode_transit')
        
        addresses = [addy, addy2]
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
        print(corString)
        print(mode)
        url2 = "https://route-and-directions.p.rapidapi.com/v1/routing"

        querystring2 = {"waypoints":corString,"mode":mode}

        headers2 = {
            "X-RapidAPI-Host": "route-and-directions.p.rapidapi.com",
            "X-RapidAPI-Key": "90a274727dmsh607a63ae7dd7473p12f953jsn5e3fb6071646"
        }

        response2 = requests.request("GET", url2, headers=headers2, params=querystring2).json()
        stri = ''
        for el in range(0, len(response2['features'][0]['properties']['legs'][0]['steps'])):
            pair = response2['features'][0]['properties']['legs'][0]['steps'][el]['instruction']
            stri += pair['text']+"\n"
        
        print(stri)
        dispatcher.utter_message(stri)
        return []
    
# round trip
class ActionSubmitFlightForm1(Action):
     
     
    def name(self) -> Text:
        return "action_flight_form1"
        
    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["departureC", "arrivalC", "departure_date", "return_date"]
    

    
    def run(self, dispatcher, tracker, domain):
        f1 = open('resources/airports_rmDuplicates.json')
        data = json.load(f1)



        departC = tracker.get_slot('departureC')
        arrivalC = tracker.get_slot('arrivalC')
        dDate = tracker.get_slot('departure_date')
        rDate = tracker.get_slot('return_date')
       
        # Get airport code from city slot name
        depart_code = 'Not found'
        arrival_code = 'Not found'

        for e in data:
            if(e['city'] == arrivalC):
                arrival_code = e['code']
            if(e['city'] == departC):
                depart_code = e['code']
                
        f1.close()
        
        #Now that you have the airport code saved int depart_code and arrival_code we can use the skypicker
        # api to aquire the flight information
        
        print(f"depart_code = {depart_code}, arrival_code = {arrival_code}, depart city = {departC}, arrival city = {arrivalC}, departureDate = {dDate}, returnDate ={rDate} ")
       
        url4 = "https://skyscanner44.p.rapidapi.com/search-extended"
        
        querystring3 = {"adults":"1","origin":"YVR","destination":"YYZ","departureDate":"2022-08-01","returnDate":"2022-08-10","currency":"CAD"}
        print(querystring3)
        headers3 = {
	        "X-RapidAPI-Host": "skyscanner44.p.rapidapi.com",
	        "X-RapidAPI-Key": "90a274727dmsh607a63ae7dd7473p12f953jsn5e3fb6071646"
            }

        response = requests.request("GET", url4, headers=headers3, params=querystring3).json()


        string_builder = ''
        temp_airlines_added = []
        i = 1

        # print(response['itineraries']['results'][0])
        # print(json.dumps(response['itineraries']['results'][0], indent=4, sort_keys=True))
        for e in response['itineraries']['results']:
            price = e['pricing_options'][0]['price']['amount']
            for ee in e['legs']:

                if(ee['origin']['displayCode'] == 'YYZ' and ee['segments'][0]['operatingCarrier']['name'] not in temp_airlines_added):
                    temp_airlines_added.append(ee['segments'][0]['operatingCarrier']['name'])

                    if(i == 1):
                        flight_num = 'Flight #{}'.format(i)
                    else:
                        flight_num = '\nFlight #{}'.format(i)

                    flight_with = 'Flying with {}'.format(ee['segments'][0]['operatingCarrier']['name'])
                    depart_on = 'Departing on {}'.format(ee['departure'][0:10] + ' @ ' + ee['departure'][-8:])
                    arriv_on = 'Arriving on {}'.format(ee['arrival'][0:10] + ' @ ' + ee['arrival'][-8:])
                    price_send = 'Which will cost you aboot: ${}'.format(price)
                    
                    string_builder += flight_num + '<br>\n'
                    string_builder += flight_with + '<br>\n'
                    string_builder += depart_on + '<br>\n'
                    string_builder += arriv_on + '<br>\n'
                    string_builder += price_send 

                    i += 1
                if(i >= 10):
                    break
       
       
        print(string_builder)
        dispatcher.utter_message(string_builder)
       
        return []
        # # For testing vv
        # response = 'Arrival code: {}, depature code {}'.format(arrival_code, depart_code)
        # dispatcher.utter_message(response)
        # # For testing ^^

        # response = 'Departure City: {}, Arrival City: {}, Departure Date: {}, Return Date: {}!!'.format(departC, arrivalC, dDate, rDate)
        
   
# one way


class ActionSubmitFlightForm2(Action):
     
     
    def name(self) -> Text:
        return "action_flight_form2"
        
    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["departureC", "arrivalC", "departure_date"]
    

    
    def run(self, dispatcher, tracker, domain):
        f1 = open('resources/airports_rmDuplicates.json')
        data = json.load(f1)



        departC = tracker.get_slot('departureC')
        arrivalC = tracker.get_slot('arrivalC')
        dDate = tracker.get_slot('departure_date')
    
    
        # Get airport code from city slot name
        depart_code = 'Not found'
        arrival_code = 'Not found'

        for e in data:
            if(e['city'] == arrivalC):
                arrival_code = e['code']
            if(e['city'] == departC):
                depart_code = e['code']
            
        f1.close()
    
    #Now that you have the airport code saved int depart_code and arrival_code we can use the skypicker
    # api to aquire the flight information
    
        print(f"depart_code = {depart_code}, arrival_code = {arrival_code}, depart city = {departC}, arrival city = {arrivalC}, departureDate = {dDate}")
    
        url = "https://skyscanner44.p.rapidapi.com/search-extended"
    
        querystring = {"adults":"1","origin":"YVR","destination":"LHR","departureDate":"2022-09-23","returnDate":"2022-08-10","currency":"CAD"}
        print(querystring)
        headers = {
            "X-RapidAPI-Host": "skyscanner44.p.rapidapi.com",
            "X-RapidAPI-Key": "90a274727dmsh607a63ae7dd7473p12f953jsn5e3fb6071646"
        }

        response = requests.request("GET", url, headers=headers, params=querystring).json()


        string_builder = ''
        temp_airlines_added = []
        i = 1


        for e in response['itineraries']['results']:
            price = e['pricing_options'][0]['price']['amount']
            for ee in e['legs']:

                if(ee['origin']['displayCode'] == 'YYZ' and ee['segments'][0]['operatingCarrier']['name'] not in temp_airlines_added):
                    temp_airlines_added.append(ee['segments'][0]['operatingCarrier']['name'])

                    if(i == 1):
                        flight_num = 'Flight #{}'.format(i)
                    else:
                        flight_num = '\nFlight #{}'.format(i)

                    flight_with = 'Flying with {}'.format(ee['segments'][0]['operatingCarrier']['name'])
                    depart_on = 'Departing on {}'.format(ee['departure'][0:10] + ' @ ' + ee['departure'][-8:])
                    arriv_on = 'Arriving on {}'.format(ee['arrival'][0:10] + ' @ ' + ee['arrival'][-8:])
                    price_send = 'Which will cost you aboot: ${}'.format(price)
                
                    string_builder += flight_num + '\n'
                    string_builder += flight_with + '\n'
                    string_builder += depart_on + '\n'
                    string_builder += arriv_on + '\n'
                    string_builder += price_send 

                    i += 1
                if(i >= 10):
                    break
    
    
        print(string_builder)
        dispatcher.utter_message(string_builder)
    
        return []