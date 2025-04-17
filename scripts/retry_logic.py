# File for API Retries

## moving old vars - will remove soon
MAX_RETRIES = 3
RETRY_DELAY = 3
MAX_API_CALLS = 500
API_COUNTER = 0

## API retries (new vars)
MAX_API_CALLS_PER_RUN = 200
MAX_API_CALLS_PER_MONTH = 2500
API_RUN_ALPHA = 0.5
API_MONTHLY_ALPHA = 0.25 ## this is essentially how much the system will tolerate before asking the user
API_MONTHLY_COUNTER_FILE = "monthly_api_counter.txt"

def wait(retry_counter, delay_time=RETRY_DELAY):
	print(f"Retrying Attempt #{retry_counter+1} in {delay_time}s...")
	time.sleep(delay_time)

def read_monthly_counter(filename=API_MONTHLY_COUNTER_FILE):
	return False

def run_with_retries():
	return False
