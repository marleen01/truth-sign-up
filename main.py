from com.dtmilano.android.viewclient import ViewClient, ViewNotFoundException
import time
import subprocess
from time import sleep
import helper
from get_mail import get_temp_email, get_message
from ui_automation import interact_with_element, wait_for_view_text, set_date, print_views
from get_phone import rent_number, get_code, mark_as_done, lease_number, parse_duration, parse_api_website, parse_country, cancel_rent
from config import adb_path, app_name
from recovery import perform_init_steps
from generate_data import get_birthdate, generate_username, generate_random_password
from decouple import config
import logging
import csv
import sys
import signal
from proxy_manager import ProxyManager
from multiprocessing import Process, freeze_support

# Create a logger object
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set the logging level

# Create a file handler that logs even debug messages
file_handler = logging.FileHandler('app.log', mode='w')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))

# Create a console handler with a higher log level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Define signal handler
def signal_handler(sig, frame):
    logger.info('Shutting down safely...')
    devices = helper.get_devices(adb_path)
    for device in devices:
        # Remove the proxy
        ProxyManager.remove_proxy(adb_path=adb_path, device_serial=device)
        logger.info(f"Removed proxy from device {device}.")
    # Kill the adb server
    logger.info('Killing the adb server...')
    subprocess.run(f'{adb_path} kill-server', shell=True)
    sys.exit(0)

def main(serialno):
    # Set the signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Perform init steps
    perform_init_steps(adb_path, app_name, device_serial=serialno)

    # Connect to the device
    device, serialno = ViewClient.connectToDeviceOrExit(serialno=serialno)

    # Create the ViewClient instance
    vc = ViewClient(device, serialno, adb=adb_path)

    # Try to touch CREATE ACCOUNT button
    interact_with_element(vc, 'CREATE ACCOUNT', adb_path, app_name, 'NEXT')

    # Try to touch NEXT button
    interact_with_element(vc, 'NEXT', adb_path, app_name, 'Enter your birth date')

    # Call the function with the desired date
    month, day, year = get_birthdate()
    birth_text = wait_for_view_text(vc, 'Enter your birth date')
    year_field = vc.findViewByIdOrRaise('android:id/numberpicker_input')
    set_date(vc, month, day, year)
    sleep(1)
    birth_text.touch()
    sleep(0.5)
    year_field.touch()
    sleep(0.5)
    # Wait for next button and click it
    interact_with_element(vc, 'NEXT', adb_path, app_name, 'Enter your email address')

    site_name = 'truthsocial.com'
    mail_type = 'OUTLOOK'

    # Call the function with the parameters you need
    email_details = get_temp_email(site=site_name, mail_type=mail_type)

    status = email_details['status']
    email_id = email_details['id']
    mail_address = email_details['mail']

    # Log requested email, id and status to a file
    with open('email_details.txt', 'a') as f:
        f.write(f'{mail_address} {email_id} {status}\n')

    # Input the email address
    email_field = vc.findViewByIdOrRaise('com.truthsocial.android.app:id/email_edit')
    email_field.setText(mail_address)
    sleep(1)

    # Click the next button
    interact_with_element(vc, 'NEXT', adb_path, app_name, 'We sent you an email')

    # Wait for the email verification link to arrive
    response = get_message(email_id, full='1')

    timeout = time.time() + 30 # 30 seconds from now
    # Returned json will have status as 'ERROR' and value as 'WAIT_LINK' if the verification link hasn't arrived yet
    # Try again every 5 seconds until the link arrives or the timeout is reached
    while True:
        if response['status'] == 'ERROR' and response['value'] == 'WAIT_LINK':
            if time.time() > timeout:
                raise Exception('Email verification failed due to timeout.')
            sleep(5)
            response = get_message(email_id, full='1')
        else:
            break

    # Parse the verification link from the response
    verify_link = helper.parse_verification(response)

    # Open the verification link in the browser
    helper.open_link(verify_link, adb_path, device_serial=serialno)
    sleep(10)
    # Generate a random password
    password = generate_random_password()
    logger.info(f"Password created: {password}")
    #views = vc.dump(window='-1')

    # Wait for the password field and input the password
    # If the password field is not found, restart
    if wait_for_view_text(vc, 'Create a password'):
        password_field = vc.findViewByIdOrRaise('com.truthsocial.android.app:id/password_edit')
        password_field.setText(password)
        sleep(1)
    else:
        logger.error('Password field not found. Restarting the program.')
        raise Exception('Email verification failed due to proxy error.')

    # Wait for the next button and click it
    interact_with_element(vc, 'NEXT', adb_path, app_name, 'Enter your phone number')

    # Parse the API website from the config file
    website = parse_api_website()

    # Below logic is special for continously retrying to rent a number if the program refuses the number
    max_attempts = 20
    rented = []
    uk_set = False
    for attempt in range(max_attempts):
        try:
            # Search for phone number text field
            if website == 'daisysms.com':
                api_key = config('DAISY_API_KEY')
                # Rent a number and parse the ID
                number_id, phone_number = rent_number(api_key, 'getNumber', 'ada', website)

            elif website == 'api.sms-activate.org':
                api_key = config('SMS_ACTIVATE_API_KEY')
                # Parse the duration from the config file
                duration = parse_duration()
                country = parse_country()
                if country == 'ENGLAND':
                    country = 16
                number_id, phone_number = lease_number(api_key, 'ada', duration, country, website)
            else:
                raise Exception('Unable to parse and set API key. Please check API keys in .env file.')

            logger.info(f"Number: {phone_number} ID: {number_id}")
            rented.append(number_id)
            sleep(5)

            if website == 'daisysms.com':
                # Input phone number
                number_field = vc.findViewByIdOrRaise('com.truthsocial.android.app:id/phone_edit')
                number_field.setText(phone_number[1:])

            elif website == 'api.sms-activate.org':
                if not uk_set:
                    # Try to set the country code
                    country_block = vc.findViewByIdOrRaise('com.truthsocial.android.app:id/country_code_block')
                    country_block.touch()

                    wait_for_view_text(vc, 'Search for country')

                    search_bar = vc.findViewWithAttributeOrRaise('class', 'android.widget.EditText')
                    search_bar.setText('United')

                    wait_for_view_text(vc, 'United Kingdom')

                    country = vc.findViewWithTextOrRaise('+44')
                    country.touch()

                    wait_for_view_text(vc, 'Enter your phone number')
                uk_set = True
                number_field = vc.findViewByIdOrRaise('com.truthsocial.android.app:id/phone_edit')
                number_field.setText(phone_number[2:])
            sleep(1)

            # Click next button
            if interact_with_element(vc, 'NEXT', adb_path, app_name, 'Verification code', max_retries=1):
                if number_id:
                    if website == 'daisysms.com':
                        # Get the code using the parsed ID
                        code_details = get_code(api_key, 'getStatus', number_id)
                        logger.info(code_details)
                        if code_details and 'STATUS_OK' in code_details:
                            # Extract the code and mark as done if needed
                            verification_code = code_details.split(':')[1]
                            result = mark_as_done(api_key, number_id, 6)  # Status 6 for marking as done
                            logger.debug(f"Mark as done result: {result}")
                    elif website == 'api.sms-activate.org':
                        # Get the code using the parsed ID
                        code_details = get_code(api_key, 'getRentStatus', number_id, website)
                        logger.info(code_details)
                        if code_details:
                            # Extract the code and mark as done if needed
                            verification_code = code_details
                            # Exit the for loop
                            break
                else:
                    logger.info("Failed to get verification code.")
                    raise Exception('Verification code failed.')
            else:
                raise Exception('Phone number is rejected by the app.')

        except Exception as e:
            logger.info(f"Attempt {attempt+1} failed: {e}")
            if attempt < max_attempts - 1:
                logger.info(f"Retrying to rent a number. Attempt {attempt+2}...")
                logger.info(f"Rented number will be cancelled: {rented[0]}")
                if website == 'api.sms-activate.org':
                    cancel_response = cancel_rent(api_key, rented[0])
                    logger.info(f"Cancel response: {cancel_response}")
                    rented.pop(0)
                continue
            else:
                logger.info(f"Max attempts reached. Restarting the program.")
                if len(rented) > 0:
                    logger.info(f"Rented number will be cancelled: {rented[0]}")
                    cancel_response = cancel_rent(api_key, rented[0])
                    logger.info(f"Cancel response: {cancel_response}")
                    rented.pop(0)
                raise Exception(f'Phone renting failed {max_attempts} times. Restarting the program.')

    sleep(5)
    # Input the verification code in the text field
    verification_field = vc.findViewByIdOrRaise('com.truthsocial.android.app:id/code_edit')
    verification_field.setText(verification_code)

    # Click next button
    interact_with_element(vc, 'NEXT', adb_path, app_name, 'Select a username')

    # Generate a random username. Example: johnsmith123, maryjane456
    username = generate_username()

    # Input the username in the text field
    # Checkbox "By continuing... "
    username_field = vc.findViewByIdOrRaise('com.truthsocial.android.app:id/username_edit')
    username_field.setText(username)
    sleep(1)

    # Click the checkbox
    checkbox_field = vc.findViewByIdOrRaise('com.truthsocial.android.app:id/checkbox')
    checkbox_field.touch()
    sleep(3)

    # Try to click on "FINISH" button and wait for "Choose a profile picture" text to appear
    interact_with_element(vc, 'FINISH', adb_path, app_name, 'Choose a profile picture')
    
    # This means that the account has been created successfully
    # Log the username and password to the file: accounts.csv
    header = ['Username', 'Password', 'PhoneNumber', 'NumberID']
    file_name = 'accounts_new.csv'
    try:
        with open(file_name, 'a', newline='') as f:
            writer = csv.writer(f)
            # Only write header if file is empty
            if f.tell() == 0:
                writer.writerow(header)
            writer.writerow([username, password, phone_number, number_id])
    except Exception as e:
        logging.error(f"Error writing to CSV file: {e}")
    
    # Log successful creation to the log file
    logger.info(f"Account created successfully. Username: {username} Password: {password}\nBeginning next account creation.")

def run():
    completions = 0
    while True:
        try:
            main()
            completions += 1
            logger.info(f"An account has been successfully created. Total accs this run: {completions}")
            sleep(3)
        except Exception as e:
            logger.error(f"An error occurred: {e}. Restarting the program.")

def run_on_device(serialno):
    completions = 0
    while True:
        try:
            main(serialno)
            completions += 1
            logger.info(f"Device {serialno}: An account has been successfully created. Total accs this run: {completions}")
            sleep(3)
        except Exception as e:
            logger.error(f"Device {serialno}: An error occurred: {e}. Restarting the program.")

def run_all_devices(devices):
    processes = []
    for serialno in devices:
        p = Process(target=run_on_device, args=(serialno,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
        
if __name__ == '__main__':
    freeze_support()
    devices = helper.get_devices(adb_path)
    run_all_devices(devices)
