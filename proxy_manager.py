import subprocess
import random
import collections
import logging
from config import adb_path
from time import sleep

logger = logging.getLogger(__name__)

class ProxyManager:
    _proxy_cycle = None

    @classmethod
    def _initialize_proxy_cycle(cls, file_path):
        """
        A class method to initialize the proxy cycle generator.
        
        :param file_path: Path to the file containing the proxies.
        """
        while True:
            with open(file_path, 'r') as f:
                proxies = f.read().splitlines()
            for proxy in proxies:
                yield proxy

    @classmethod
    def set_proxy(cls, adb_path, device_serial, file_path='proxy.txt'):
        """
        Sends an ADB command to set the global proxy on the device using the next proxy from the cycle.
        
        :param adb_path: Path to the adb executable.
        :param file_path: Path to the file containing the proxies.
        :param device_serial: The serial number of the device.
        Command example:
        adb shell settings put global http_proxy 192.168.225.100:3128
        adb shell settings put global global_http_proxy_host 192.168.225.100
        adb shell settings put global global_http_proxy_port 3128
        adb shell settings put global global_http_proxy_username foo
        adb shell settings put global global_http_proxy_password bar
        """
        # Initialize the proxy cycle generator if it hasn't been already
        if cls._proxy_cycle is None:
            cls._proxy_cycle = cls._initialize_proxy_cycle(file_path)

        try:
            # Get the next proxy from the generator
            proxy = next(cls._proxy_cycle)
            host, port = proxy.split(':')
            
            # Commands to set the proxy
            commands = [
            f'{adb_path} -s {device_serial} shell settings put global http_proxy {host}:{port}'
            ]

            # Execute each command
            for cmd in commands:
                result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output = result.stdout.decode('utf-8')
                error = result.stderr.decode('utf-8')

                if result.returncode == 0:
                    print(f'Proxy set to {proxy}: Command executed successfully', output)
                else:
                    print(f'Failed to set proxy {proxy}: An error occurred', error)

        except FileNotFoundError:
            logger.exception("The proxy.txt file was not found.")
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")

    @classmethod
    def remove_proxy(cls, adb_path, device_serial):
        """
        Clears the global proxy on the device.
        
        :param adb_path: Path to the adb executable.
        :param device_serial: The serial number of the device.
        """
        try:
            # Construct the ADB command to clear the global proxy
            adb_command = f'{adb_path} -s {device_serial} shell settings put global http_proxy :0'

            # Run the command
            result = subprocess.run(adb_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Check the output and error
            output = result.stdout.decode('utf-8')
            error = result.stderr.decode('utf-8')

            if result.returncode == 0:
                print('Proxy removed successfully:', output)
            else:
                print('An error occurred while removing the proxy:', error)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
    @classmethod
    def rotate_proxies(cls, file):
        """
        Rotates the list of proxies to change the first proxy in line.

        :param file: Path to the proxy file.
        """
        try:
            with open(file, 'r') as f:
                proxies = f.read().splitlines()  # Read the current list of proxies

            # Rotate the list
            proxies = collections.deque(proxies)
            proxies.rotate(-1)  # Rotate left; the first element goes to the end
            proxies = list(proxies)

            with open(file, 'w') as f:
                f.writelines('\n'.join(proxies) + '\n')  # Write the updated list back to the file

        except FileNotFoundError:
            print("The proxy.txt file was not found.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

#ProxyManager.remove_proxy(adb_path)
#ProxyManager.set_proxy(adb_path)