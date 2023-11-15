import requests
from requests.exceptions import RequestException
from decouple import config
from bs4 import BeautifulSoup
from urllib.parse import urlencode

# Replace the API_KEY in the .env file with your own
API_KEY = config('KOPEECHKA_API_KEY')

def send_kopeechka_request(base_url, additional_params):
    # Base parameters that are common for all requests.
    params = {
        'token': API_KEY,
        'api': '2.0',
        'type': 'JSON'  # Default response type.
    }

    # Update with additional parameters specific to the endpoint.
    params.update(additional_params)

    # Remove None values, these are optional parameters.
    params = {k: v for k, v in params.items() if v is not None}

    # Construct the full URL with parameters.
    url = base_url + urlencode(params)

    # Make the GET request.
    response = requests.get(url)

    # Return the response JSON.
    return response.json()

def get_temp_email(site, mail_type, password=0, regex=None, subject=None, investor=None, soft_id=None):
    additional_params = {
        'site': site,
        'mail_type': mail_type,
        'password': password,
        'regex': regex,
        'subject': subject,
        'investor': investor,
        'soft_id': soft_id
    }

    return send_kopeechka_request('https://api.kopeechka.store/mailbox-get-email?', additional_params)

def get_message(task_id, full=None):
    additional_params = {
        'id': task_id,
        'full': full
    }

    return send_kopeechka_request('https://api.kopeechka.store/mailbox-get-message?', additional_params)

