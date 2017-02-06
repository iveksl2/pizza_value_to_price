import requests 
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as plt
import yaml

# Do not need Oauth to access venue data. 
# Get Foursquare Client ID & Client Secret here: https://developer.foursquare.com/ 
with open('config.yml', 'r') as ymlfile:
	config = yaml.load(ymlfile)

def get_venues(foursquare_base_json):
	"""base foursquare explore endpoint json -> venue items hash"""
	return foursquare_base_json['response']['groups'][0]['items']

def get_venue_data(venue_json):
	"""Extracts the name, price & rating from a venue
	   Note: Will not handle missing data
	"""
	name   = venue_json['venue']['name']
	rating = venue_json['venue']['rating']
	price  = venue_json['venue']['price']['tier']
	return {'name': name, 
	        'rating': rating,
            'price': price}

endpoint = 'https://api.foursquare.com/v2/venues/explore?'
#The exact lattitude and longitude of the meetup was not used to protect the identity of organizer. 
#For reproducibility these coordinates can be used. Obtained via Google (Chicago, IL)
payload = {'ll': '41.8781,-87.6298',
		   'query': 'pizza', 
		   'limit': 25, 
		   'client_id': config['client_id'],
		   'client_secret': config['client_secret'],
		   'v':'20170205'} #need to update when run. Can make dynamic

foursquare_response = requests.get(endpoint, params = payload)
venues = get_venues(foursquare_response.json())
venue_dat = map(get_venue_data, venues)
venues_df = pd.DataFrame(list(venue_dat))
venues_df.set_index(keys = ['name'], drop = True, inplace = True)
venues_df.drop(['Potbelly Sandwich Shop', "Luke's Italian Beef"], inplace = True) # manual
venues_df

# Higher rated pizza tends to be a bit more expensive. However we want to maximize our dollar
# venues_df.groupby(['price'])['rating'].agg({'Average_Rating': np.mean, 'Size': np.size})
sns.jointplot(x="price", y="rating", data=venues_df);

venues_df = venues_df.rename(columns = {'rating': 'value'})
venues_df['value_to_price'] = venues_df['value'] / venues_df['price'] 
venues_df = venues_df.sort_values(by = ['value_to_price'])
venues_df['value_to_price'].plot(kind='barh', title="Chicago Pizza's Value to Price Ratio")

# Include methogological issue's here. Thank organizers and speaker, lets eat. woot woot
