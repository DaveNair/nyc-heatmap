# File for API Retries
import time
import random
from datetime import datetime

## moving old vars - will remove soon
MAX_RETRIES_PER_ENTRY = 3
RETRY_DELAY = 3
MAX_API_CALLS = 500
API_COUNTER = 0
RETRY_BACKOFF = [1, 2, 5]  # seconds

'''
Google Maps API has a free-usage quota of 200$ per month, at $0.005 per API call:
- Limit = 200$/month * (1 call / $0.005) = 40k calls per month - 10k haircut
=> 30k calls per month
=> 1k calls per day
'''

## API retries (new vars)
MAX_API_CALLS_PER_RUN = 200
MAX_API_CALLS_PER_DAY = 2000
MAX_API_CALLS_PER_MONTH = 10000
API_RUN_ALPHA = 1
API_DAILY_ALPHA = 1
API_MONTHLY_ALPHA = 0.25 ## this is essentially how much the system will tolerate before asking the user
API_MONTHLY_COUNTER_FILE = "monthly_api_counter.log"
CALLS_PER_STATUS_MSG = 100
VERBOSE = True

ERROR_LOG_FILE = 'retry_errors.log'

## === SETTING SOME VARS ===
eMAX_API_PER_RUN = MAX_API_CALLS_PER_RUN*API_RUN_ALPHA
eMAX_API_PER_DAY = MAX_API_CALLS_PER_DAY*API_DAILY_ALPHA
eMAX_API_PER_MONTH = MAX_API_CALLS_PER_MONTH*API_MONTHLY_ALPHA

MIN_API_LIMIT = min([
	eMAX_API_PER_RUN, 
	# eMAX_API_PER_DAY, ## if all goes well, I don't actually care about this number 
	eMAX_API_PER_MONTH
	])

API_RUN_COUNTER = 0 ## just to initialize; this gets reset in main

def wait(retry_counter, delay_time=RETRY_DELAY):
	print(f"Retrying Attempt #{retry_counter+1} in {delay_time}s...")
	time.sleep(delay_time)

def read_counter(filename=API_MONTHLY_COUNTER_FILE):
	try:
		with open(filename, 'r') as f:
			lines = f.readlines()
	except FileNotFoundError:
		return 0
	
	for line in reversed(lines):
		if line.strip():  # Skip blank lines
			try:
				return int(line.split(':')[-1].strip())
			except (IndexError, ValueError):
				return 0  # Malformed line
	return 0  # File had no valid lines

def write_counter(filename=API_MONTHLY_COUNTER_FILE):
	counter_msg = f"{datetime.now()}: {PERSISTED_COUNTER}\n"
	with open(filename, 'a') as f:
		f.write(counter_msg)
	pass

def get_counter():
	return PERSISTED_COUNTER

def increment_counters():
	'''This increments BOTH counters.'''
	global API_RUN_COUNTER, PERSISTED_COUNTER
	API_RUN_COUNTER += 1
	PERSISTED_COUNTER += 1
	pass

def reset_run_counter():
	global API_RUN_COUNTER
	API_RUN_COUNTER = 0
	pass

def _write_error_log(entry, log_file=ERROR_LOG_FILE):
	with open(log_file, "a") as f:
		f.write(f"{entry}\n")

def run_with_retries(fn, log_label='', retry_statuses=None, extract_status_fn=None):
	for attempt in range(MAX_RETRIES_PER_ENTRY):
		try:
			result = fn()
			## going to check through a set list of statuses - unless they are not there
			if retry_statuses and extract_status_fn:
				current_status = extract_status_fn(result)
				if current_status in retry_statuses:
					## create wait_time, print, log, and wait
					wait_time = RETRY_BACKOFF[attempt] + random.uniform(0, 0.5)
					print(f"[Retryable status condition] {status} - Retrying... (Attempt {attempt+1})")
					_write_error_log(f"[{datetime.now()}] Retrying API Call - {status} - {log_label} (Attempt {attempt+1})")
					time.sleep(wait_time)
					continue # try again 
			return result

		except Exception as e:
			wait_time = RETRY_BACKOFF[attempt] + random.uniform(0, 0.5)
			error_entry = f"[{datetime.now()}] {log_label} - Retry {attempt+1}/{MAX_RETRIES_PER_ENTRY} failed: {e}. Waiting {wait_time:.1f}s..."
			print(error_entry)
			_write_error_log(error_entry)
			time.sleep(wait_time)

	raise RuntimeError(f"{log_label} Exceeded max number of retries ({MAX_RETRIES_PER_ENTRY}). Aborting to prevent billing.")
	return False

PERSISTED_COUNTER = read_counter()

def call_api_with_limits(df_row):
	from commute import get_google_time
	from constants import BAD_VAL
	'''This just wraps our google time API with a function that watches for our API Limits (mostly to keep us in free-tier)'''
	## quick decline function
	def decline_api_call():
		run_perc = float(API_RUN_COUNTER) / eMAX_API_PER_RUN
		monthly_perc = float(PERSISTED_COUNTER) / eMAX_API_PER_MONTH
		run_string = f"{API_RUN_COUNTER}/{eMAX_API_PER_RUN} ({run_perc*100:.1f}%)"
		month_string = f"{PERSISTED_COUNTER}/{eMAX_API_PER_MONTH} ({monthly_perc*100:.1f}%)"
		print(f"You have exceeded your API Limits:\n\tRun Limit: \t{run_string}\n\tMonth Limit: \t{month_string}\nExiting to avoid billing.")
		return BAD_VAL

	## check if limits are hit, & continue
	if API_RUN_COUNTER>eMAX_API_PER_RUN or PERSISTED_COUNTER>eMAX_API_PER_MONTH:
		decline_api_call()
	output_time = get_google_time(df_row['lat'], df_row['lon'])
	## if everything worked, increment our counters
	increment_counters()
	if VERBOSE and API_RUN_COUNTER%CALLS_PER_STATUS_MSG==0:
		print(f"\tFinished {API_RUN_COUNTER} API calls...")
	return output_time
