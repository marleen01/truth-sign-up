import subprocess
import json
import logging

logger = logging.getLogger(__name__)

def tap_screen(x, y, adb_path, device_serial):
    """
    Sends an ADB command to simulate a tap on the screen at the given x, y coordinates.

    :param adb_path: Path to the adb executable.
    :param x: The x coordinate on the screen.
    :param y: The y coordinate on the screen.
    :param device_serial: The serial number of the device.
    """
    adb_command = f'{adb_path} -s {device_serial} shell input tap {x} {y}'
    
    # Run the command
    result = subprocess.run(adb_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Check the output and error
    output = result.stdout.decode('utf-8')
    error = result.stderr.decode('utf-8')
    
    if result.returncode == 0:
        logger.info(f'Command executed successfully: {output}')
    else:
        logger.error(f'An error occurred: {error}')

def type_text(text, adb_path, device_serial):
    """
    Sends an ADB command to simulate typing text on the device.

    :param adb_path: Path to the adb executable.
    :param text: The text to type on the device.
    :param device_serial: The serial number of the device.
    """
    # Escape spaces with %s
    escaped_text = text
    adb_command = f'{adb_path} -s {device_serial} shell input text "{escaped_text}"'
    
    # Run the command
    result = subprocess.run(adb_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Check the output and error
    output = result.stdout.decode('utf-8')
    error = result.stderr.decode('utf-8')
    
    if result.returncode == 0:
        logger.info(f'Text typed successfully: {output}')
    else:
        logger.error(f'An error occurred: {error}')

def long_tap_screen(x, y, adb_path, device_serial, duration=1500):
    """
    Sends an ADB command to simulate a long tap on the screen at the given x, y coordinates.

    :param adb_path: Path to the adb executable.
    :param x: The x coordinate on the screen.
    :param y: The y coordinate on the screen.
    :param device_serial: The serial number of the device.
    :param duration: Duration of the long tap in milliseconds. Default is 1500.
    """
    adb_command = f'{adb_path} -s {device_serial} shell input swipe {x} {y} {x} {y} {duration}'
    
    # Run the command
    result = subprocess.run(adb_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Check the output and error
    output = result.stdout.decode('utf-8')
    error = result.stderr.decode('utf-8')
    
    if result.returncode == 0:
        logger.info(f'Long tap executed successfully: {output}')
    else:
        logger.error(f'An error occurred: {error}')

def open_link(url_link, adb_path, device_serial):
    """
    Sends an ADB command to open a link in the default browser.

    :param adb_path: Path to the adb executable.
    :param url_link: The URL to open in the browser.
    :param device_serial: The serial number of the device.
    """
    adb_command = f'{adb_path} -s {device_serial} shell am start -a android.intent.action.VIEW -d {url_link}'
    
    # Run the command
    result = subprocess.run(adb_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Check the output and error
    output = result.stdout.decode('utf-8')
    error = result.stderr.decode('utf-8')
    
    if result.returncode == 0:
        logger.info(f'Link opened successfully: {output}')
    else:
        logger.error(f'An error occurred: {error}')

def clear_app_data(package_name, adb_path, device_serial):
    cmd = f"{adb_path} -s {device_serial} shell pm clear {package_name}"
    subprocess.run(cmd.split())

def launch_app(package_name, adb_path, device_serial):
    cmd = f"{adb_path} -s {device_serial} shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1"
    subprocess.run(cmd, shell=True)

def go_to_home_screen(adb_path, device_serial):
    """
    Sends an ADB command to simulate a home button press on the device.

    :param adb_path: Path to the adb executable.
    :param device_serial: The serial number of the device.
    """
    cmd = f"{adb_path} -s {device_serial} shell input keyevent KEYCODE_HOME"
    subprocess.run(cmd, shell=True)

def parse_verification(response):
    """
    Parses the verification link from the response.
    :param response: The response from the get_message() function.
    :return: The verification link.
    """

    # Parse the HTML content
    response_st = response['fullmessage']
    # Define the verification link beginning part
    verification_link_beginning = "http://truthsocial.com/v1/verify_email"
    # Find the start of the verification link
    verification_link_start = response_st.find(verification_link_beginning)
    
    if verification_link_start != -1:
        # Find the end of the verification link
        verification_link_end = response_st.find("\"", verification_link_start)
        
        if verification_link_end != -1:
            # Extract the verification link
            verification_link = response_st[verification_link_start:verification_link_end]
            return verification_link
        else:
            # End delimiter not found
            logger.error('Verification link end not found.')
            return None

    else:
        # Verification link not found
        logger.error('Verification link not found.')
        return None

def get_devices(adb_path):
    """
    Gets the list of connected devices.

    :param adb_path: Path to the adb executable.
    :return: The list of connected devices.
    """
    # ADB command to get the list of connected devices
    cmd = f'{adb_path} devices'
    result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    devices = []
    for line in output.splitlines():
        if line.endswith('device'):
            device = line.split('\t')[0]
            devices.append(device)
    return devices