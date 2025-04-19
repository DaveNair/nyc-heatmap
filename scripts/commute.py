import os
import requests
from datetime import datetime
import time
import numpy as np
from dotenv import load_dotenv
load_dotenv() ## this will load the .env contents into env
from lib.utils import log_error
from constants import BAD_VAL
import retry_logic as retry 
from retry_logic import run_with_retries

CHOSEN_DEPARTURE = 'tomorrow'
VERBOSE = False

## Loading the key
google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

def get_google_time(origin_lat, origin_lon, 
		destination="Times Square, New York, NY",
		# destination="40 Ludlow St, New York, NY 10002", 
		departure_time=True):
	# global google_api_key, VERBOSE, MAX_RETRIES, CHOSEN_DEPARTURE ## << i dont think this is needed ?
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
	## build request sender
	def call_api():
		response = requests.get(url)
		return response.json() # ie - data

	def extract_google_status(json_data):
		return json_data.get('status')

	result = run_with_retries(
		call_api,
		log_label=f"({origin_lat},{origin_lon})",
		retry_statuses=['UNKNOWN_ERROR'],
		extract_status_fn=extract_google_status
		)
	status = result.get('status')

	## after we move on w a successful (non-retry) result
	if status == 'OK':
		return round(result["routes"][0]["legs"][0]["duration"]["value"] / 60, 2)
	elif status == 'ZERO_RESULTS':
		if VERBOSE: print(f"No transit route found for ({origin_lat:.4f},{origin_lon:.4f})")
		return np.nan

	## after this, we should be recording the error
	error_message = f"[{status}] - {url}"
	log_error(error_message)
	if status in ["NOT_FOUND", "MAX_WAYPOINTS_EXCEEDED", "INVALID_REQUEST", "OVER_QUERY_LIMIT"]:
		return BAD_VAL
	elif status == 'REQUEST_DENIED':
		raise RuntimeError("API Access was rejected. Check API key & permissions. Exiting.")
	else:
		print(f"API Error: {result['status']} for ({origin_lat:.4f},{origin_lon:.4f}), after finishing retry_logic.run_with_retries()...")
		return BAD_VAL

## example lat/lon (from NTA data)
# origin_lat = 40.7831
# origin_lon = -73.9712  # e.g., Upper West Side
# print(get_google_time(origin_lat, origin_lon))
