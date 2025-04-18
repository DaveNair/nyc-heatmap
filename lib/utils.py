## Utils & Common functions
from datetime import datetime

def log_error(message, filename='errors.log'):
	with open(filename, 'a') as f:
		f.write(f"{datetime.now()}: {message}\n")

def tempfile(prefix='tempfile-', suffix='.txt'):
	return f"{prefix}{datetime.now()}{suffix}"
