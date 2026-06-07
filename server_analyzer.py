import os
from dotenv import load_dotenv
import requests
import time
# Read variables from the .env file and add them to your system environment
load_dotenv() 

healthy = os.getenv('HEALTHY')
slow = os.getenv('SLOW')
failing = os.getenv('FAILING')
valid = os.getenv('VALID')
url = [healthy,slow,failing,valid]
url_times = []
response = requests.get(healthy)
print({url:healthy,status_code:response.status_code})
for i in url:
    start = time.perf_counter()
    response = requests.get(i)
    end = time.perf_counter()
    url_times.append({
        'url':i,
        'status_code':response.status_code,
        'response_time':end-start})