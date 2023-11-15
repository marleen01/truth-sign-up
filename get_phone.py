import requests
from requests.exceptions import RequestException
from decouple import config
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import time

API_KEY = config('DAISY_API_KEY')

def rent_number(api_key, action, service):
    url = "https://daisysms.com/stubs/handler_api.php"
    params = {"api_key": api_key, "action": action, "service": service}
    response = requests.get(url, params=params)
    response_parts = response.text.split(':')
    if response_parts[0] == 'ACCESS_NUMBER':
        number_id = response_parts[1]
        phone_number = response_parts[2]
        return number_id, phone_number
    else:
        return None, None  # Handle error cases or re-raise an exception


def get_code(api_key, action, id, max_retries=13):
    url = "https://daisysms.com/stubs/handler_api.php"
    for _ in range(max_retries):
        params = {"api_key": api_key, "action": action, "id": id}
        response = requests.get(url, params=params)
        code_details = response.text
        if 'STATUS_OK' in code_details:
            return code_details
        elif 'STATUS_WAIT_CODE' in code_details:
            print('Waiting for code...')
            time.sleep(3)
        else:
            break  # In case of other statuses like NO_ACTIVATION, STATUS_CANCEL
    raise Exception('Failed to get code.')

def mark_as_done(api_key, id, status):
    url = "https://daisysms.com/stubs/handler_api.php"
    params = {"api_key": api_key, "action": "setStatus", "id": id, "status": status}
    response = requests.get(url, params=params)
    return response.text