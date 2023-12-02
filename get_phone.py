import requests
from requests.exceptions import RequestException
from decouple import config
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import time
import logging

logger = logging.getLogger(__name__)

API_KEY = config('DAISY_API_KEY')

def parse_duration():
    with open('config.txt', 'r') as f:
        # Parse duration from string like "4H" or "1D", number + H/D, convert to hours
        sms_duration = f.readline().split('=')[1].strip()
        num_part = sms_duration[:-1]
        unit_part = sms_duration[-1]
        duration = int(num_part)
        logger.debug(f"SMS duration: {duration} {unit_part}")
        if unit_part == 'H':
            return duration
        elif unit_part == 'D':
            return duration * 24
        else:
            raise Exception('Invalid duration format.')

def parse_api_website():
    with open('config.txt', 'r') as f:
        # Parse api website from second line of config.txt, looks like "API_TO_USE=SMS_ACTIVATE"
        website = f.readlines()[1].split('=')[1].strip()
        if website == 'SMS_ACTIVATE':
            return 'api.sms-activate.org'
        elif website == 'DAISY':
            return 'daisysms.com'
        else:
            raise Exception('Invalid API website.')

def parse_country():
    with open('config.txt', 'r') as f:
        # Parse country from third line of config.txt, looks like "COUNTRY=ENGLAND"
        country = f.readlines()[2].split('=')[1].strip()
        return country

def rent_number(api_key, action, service, website):
    url = "https://" + website + "/stubs/handler_api.php"
    params = {"api_key": api_key, "action": action, "service": service}
    response = requests.get(url, params=params)
    response_parts = response.text.split(':')
    if response_parts[0] == 'ACCESS_NUMBER':
        number_id = response_parts[1]
        phone_number = response_parts[2]
        return number_id, phone_number
    else:
        return None, None  # Handle error cases or re-raise an exception

def lease_number(api_key, service, rent_time, country, website):
    # The response of the service will be in json format, example:
    # { "status": "success", "phone": { "id": 1049, "endDate": "2020-01-31T12:01:52", "number": "79959707564" } }
    url = "https://" + website + "/stubs/handler_api.php"
    params = {"api_key": api_key, "action": "getRentNumber", "service": service, "rent_time": rent_time, "country": country}
    response = requests.get(url, params=params)
    response_json = response.json()
    if response_json['status'] == 'success':
        number_id = response_json['phone']['id']
        phone_number = response_json['phone']['number']
        return number_id, phone_number
    else:
        raise Exception('Failed to lease number. Response: ' + response.text)

def get_code(api_key, action, id, website, max_retries=13):
    url = "https://" + website + "/stubs/handler_api.php"
    for _ in range(max_retries):
        params = {"api_key": api_key, "action": action, "id": id}
        response = requests.get(url, params=params)
        if website == 'daisysms.com':
            code_details = response.text
            if 'STATUS_OK' in code_details:
                return code_details
            elif 'STATUS_WAIT_CODE' in code_details:
                logger.info('Waiting for code...')
                time.sleep(3)
            else:
                break  # In case of other statuses like NO_ACTIVATION, STATUS_CANCEL
        elif website == 'api.sms-activate.org':
            #The response of the service will be in json format, example:
            #{ "status": "success", "quantity": "2", "values": { "0": { "phoneFrom": "79180230628", "text": "5", "service": "ot", "date": "2020-01-30 14:31:58" }, "1": { "phoneFrom": "79180230628", "text": "4", "service": "ot", "date": "2020-01-30 14:04:16" } } }
            #* successful only if there is an SMS (field 'quantity'> 0).
            response_json = response.json()
            if response_json['status'] == 'success':
                values = response_json['values']
                return values['0']['text']
            elif response_json['status'] == 'error' and response_json['message'] == 'STATUS_WAIT_CODE':
                logger.info('Waiting for code...')
                time.sleep(3)
            else:
                break
        raise Exception('Failed to get code.')

def mark_as_done(api_key, id, status, website):
    url = "https://" + website + "/stubs/handler_api.php"
    params = {"api_key": api_key, "action": "setStatus", "id": id, "status": status}
    response = requests.get(url, params=params)
    return response.text
