## Utils & Common functions
from datetime import datetime

def log_error(message, filename='errors.log', timestamp=True):
	if timestamp==True:
		timestamp = f"{datetime.now()}:"
	with open(filename, 'a') as f:
		f.write(f"{timestamp} {message}\n")

def tempfile(prefix='tempfile-', suffix='.txt'):
	return f"{prefix}{datetime.now()}{suffix}"
