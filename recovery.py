# This file contains functions that define recovery actions.
import time
from proxy_manager import ProxyManager
from helper import go_to_home_screen, clear_app_data, launch_app
import logging

logger = logging.getLogger(__name__)

def perform_init_steps(adb_path, app_name, device_serial):
    """
    Performs a series of init steps: goes to the home screen, clears the app data,
    shuffles proxy file, sets a new proxy, and then relaunches the app. This is useful
    for when proxy errors, or when a new account needs to be created.

    :param adb_path: Path to the adb executable.
    :param app_name: Name of the application package.
    """
    # Go to the home screen
    go_to_home_screen(adb_path, device_serial)
    time.sleep(1)
    logger.info('Going to home screen...')

    # Clear the application's data
    clear_app_data(app_name, adb_path, device_serial)
    time.sleep(1)
    logger.info('Clearing app data...')

    # Rotate the proxy file
    ProxyManager.rotate_proxies('proxy.txt')
    time.sleep(1)

    # Set a new proxy
    ProxyManager.set_proxy(adb_path, device_serial)
    time.sleep(1)
    logger.info('Setting new proxy...')

    # Launch the application
    launch_app(app_name, adb_path, device_serial)
    time.sleep(1)
    logger.info('Launching the application...')