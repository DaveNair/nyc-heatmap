# File for API Retries
import time
import random
from datetime import datetime

## moving old vars - will remove soon
MAX_RETRIES = 3
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
API_RUN_ALPHA = 0.5
API_DAILY_ALPHA = 0.5
API_MONTHLY_ALPHA = 0.25 ## this is essentially how much the system will tolerate before asking the user
API_MONTHLY_COUNTER_FILE = "monthly_api_counter.log"

ERROR_LOG_FILE = 'retry_errors.log'

## === SETTING SOME VARS ===
MIN_API_LIMIT = min([MAX_API_CALLS_PER_RUN*API_RUN_ALPHA, MAX_API_CALLS_PER_DAY*API_DAILY_ALPHA, MAX_API_CALLS_PER_MONTH*API_MONTHLY_ALPHA])


def wait(retry_counter, delay_time=RETRY_DELAY):
	print(f"Retrying Attempt #{retry_counter+1} in {delay_time}s...")
	time.sleep(delay_time)

def read_monthly_counter(filename=API_MONTHLY_COUNTER_FILE):
	print(f"DO THIS")
	sys.exit(1)
	return False

def _write_error_log(entry, log_file=ERROR_LOG_FILE):
	with open(log_file, "a") as f:
		f.write(f"{entry}\n")

def run_with_retries(fn, log_label='', retry_statuses=None, extract_status_fn=None):
	for attempt in range(MAX_RETRIES):
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
			error_entry = f"[{datetime.now()}] {log_label} - Retry {attempt+1}/{MAX_RETRIES} failed: {e}. Waiting {wait_time:.1f}s..."
			print(error_entry)
			_write_error_log(error_entry)
			time.sleep(wait_time)

	raise RuntimeError(f"{log_label} Exceeded max number of retries ({MAX_RETRIES}). Aborting to prevent billing.")
	return False
