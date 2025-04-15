import os
import requests
from datetime import datetime
import time
from dotenv import load_dotenv
load_dotenv() ## this will load the .env contents into env

CHOSEN_DEPARTURE = 'tomorrow'

MAX_RETRIES = 3
RETRY_DELAY = 3
MAX_API_CALLS = 500
API_COUNTER = 0
VERBOSE = False

## Loading the key
google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

def wait_and_retry(retry_counter, delay_time=RETRY_DELAY):
	print(f"Retrying Attempt #{retry_counter+1} in {delay_time}s...")
	time.sleep(delay_time)

def get_google_time(origin_lat, origin_lon, 
		# destination="Times Square, New York, NY",
		destination="40 Ludlow St, New York, NY 10002", 
		departure_time=True):
	global google_api_key, VERBOSE, MAX_RETRIES, CHOSEN_DEPARTURE
	if departure_time in [True,False,'DEFAULT','default']:
		if CHOSEN_DEPARTURE == 'now':
			departure_time = int(datetime.now().timestamp())
		elif CHOSEN_DEPARTURE == 'tomorrow':
			## Departure time: 8:00 AM tomorrow to avoid transit gaps
			departure = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
			departure_time = int(time.mktime(departure.timetuple()))
	## build the url
	url = (
		"https://maps.googleapis.com/maps/api/directions/json?"
		f"origin={origin_lat},{origin_lon}"
		f"&destination={destination}"
		f"&mode=transit"
		f"&departure_time={departure_time}"
		f"&key={google_api_key}"
	)
	## send the request
	## adding retries
	for retry_attempt in range(MAX_RETRIES):
		if API_COUNTER > MAX_API_CALLS:
			print(f"Max API Calls reached. Aborting to prevent billing.")
			return None

		response = requests.get(url)
		data = response.json()
		status = data['status']
		
		if status == 'OK':
			duration_sec = data["routes"][0]["legs"][0]["duration"]["value"]
			duration_min = duration_sec // 60
			if VERBOSE==True:
				print(f"Estimated commute time: {duration_min} minutes")
			return duration_min	
		
		elif status == 'ZERO_RESULTS':
			if VERBOSE: print(f"No transit route found for ({origin_lat:.4f},{origin_lon:.4f})")
			return None
		
		elif status in ['OVER_QUERY_LIMIT', 'UNKNOWN_ERROR']:
			wait_and_retry(API_COUNTER) 
		else:
			print(f"API Error: {status} for ({origin_lat:.4f},{origin_lon:.4f}), after {retry_attempt} attempts")
			break
		return None

## example lat/lon (from NTA data)
# origin_lat = 40.7831
# origin_lon = -73.9712  # e.g., Upper West Side
# print(get_google_time(origin_lat, origin_lon))
