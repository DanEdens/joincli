import argparse
import json
import os
import socket
import sys
import urllib.request
from json import JSONDecodeError

import requests

import joincliUtils
from . import logger


class ArgText:
    main: str = f"\nSetup Module for the Join-CLI\n"
    apikey: str = f"Accepts Join Api token, get yours at " \
                  f"https://joinjoaomgcd.appspot.com/"
    register: str = "Register this client with Join "
    update: str = "Updates your Join device List"
    debug: str = 'Set logging level to Debug'


class Formatter(argparse.RawDescriptionHelpFormatter):
    """argparse.RawDescriptionHelpFormatter
        Provides formatting settings for argument "Help" messages.
        Can add argparse.ArgumentDefaultsHelpFormatter for defaults.
    """
    pass


parser = argparse.ArgumentParser(
        description=ArgText.main,
        prog='JoinCLI',
        formatter_class=Formatter
        )

parser.add_argument("-ak", "--apikey",
                    help=ArgText.apikey,
                    type=joincliUtils.api_regex)

parser.add_argument("-up", "--update", action='store_true', default=False,
                    help=ArgText.update)

parser.add_argument("-re", "--register", help=ArgText.register,
                    action='store_true', default=False)

parser.add_argument('-d', '--debug', action='store_true', default=False,
                    help=ArgText.debug)

arguments = parser.parse_args()


def open_remote_devices(apikey=os.getenv('JOIN_API')):
    """

    :param apikey:
    :return:
    """
    try:
        _devices = urllib.request.urlopen(
                "https://joinjoaomgcd.appspot.com/_ah/api"
                "/registration/v1/listDevices?apikey=" +
                apikey).read()
        try:
            return json.loads(joincliUtils.decode_UTF8(_devices))
        except JSONDecodeError as e:
            raise Exception(f'Open remote devices using '
                            f'API key has failed:\n'
                            f'Error code: {e.code}: \n{e}')

    except urllib.error.HTTPError as e:
        raise Exception(f"Error code: {e.code}: \n{e}")
    except urllib.error.URLError as e:
        raise Exception(f"Are you connected to the internet?\n"
                        f"Check your connection and try again:\n"
                        f"Error code: {e.code}: \n{e}")


def setup_devices(device):
    """
    If devices.json already exists

    :param _arguments:
    :param device:
    """
    if device is not None:
        if arguments.update:
            update_devices(device)
            sys.exit(1)
        else:
            logger.info(
                "Apikey already exists, use argument -up to update devices!")
            sys.exit(1)

    data = open_remote_devices(arguments.apikey)

    if data['success']:
        device_data = {"apikey": arguments.apikey}

        logger.info("Registered devices under apikey: ")
        for item in data["records"]:
            device_data[item["deviceName"]] = {}
            device_data[item["deviceName"]]['deviceId'] = item['deviceId']
            device_data[item["deviceName"]]['deviceType'] = item['deviceType']
            logger.info(item["deviceName"])

        pref = input("Choose the prefered device: ")
        while pref not in device_data:
            logger.info("Device not listed as registered, try again:")
            pref = input("Choose the prefered device: ")

        device_data["pref"] = pref

        data = str(json.dumps(device_data, sort_keys=True, indent=4))

        with open("devices.json", "w") as f:
            f.write(data)
            f.close()

        logger.info("Device data gattered sussesfully!")
        sys.exit(1)

    else:
        logger.info(f"Error returned from server: {data['errorMessage']}")
        logger.info("Are you sure your API key is correct?")
        sys.exit(1)


def update_devices(device):
    """

    :param device:
    """
    devices_update = open_remote_devices(device["apikey"])

    if devices_update['success']:
        device_data = {"apikey": device["apikey"]}

        for item in devices_update["records"]:
            device_data[item["deviceName"]] = {}
            device_data[item["deviceName"]]['deviceId'] = item['deviceId']
            device_data[item["deviceName"]]['deviceType'] = item['deviceType']
            # TODO Add another fields if needed

        device_data["pref"] = device["pref"]

        data = json.dumps(device_data, sort_keys=True, indent=4)

        with open("devices.json", "w") as f:
            f.write(str(data))

        logger.info("Device data updated sussesfully!")
        sys.exit(1)


def register_new_device(device):
    """
    Device Type Codes:
    Android:    1
    Chrome:     3
    Windows:    4
    Firefox:    6
    IFFT:       12
    Node-red:   13
    """
    url: str = "https://joinjoaomgcd.appspot.com/_ah/api/registration/v1/registerDevice/"
    headers = {'content-type': 'application/json'}
    port: str = str(input(
            f"Which port should I listen to? [Default: 1820]"
            ) or os.getenv('JOIN_PORT', 1820))
    name: str = str(input(
            f"Name this device: [Default: {socket.gethostname()}]"
            ) or socket.gethostname())

    logger.info("Obtaining IP address...")
    ip_local = f"{socket.gethostbyname(socket.gethostname())}:{port}"
    ip_external = f"{requests.get('https://api.ipify.org').text}:{port}"

    reg = {
            "apikey":     device["apikey"],
            "deviceName": name,
            "regId":      ip_external,
            "regId2":     ip_local,
            "deviceType": "13"
            }

    logger.info("Sending request...")

    try:
        response = requests.post(url, json.dumps(reg), headers=headers)
        response = response.json()
    except requests.exceptions.HTTPError:
        logger.warning(f"Error message: {response['errorMessage']}")
        raise

    # TODO handle device already registered
    update_devices(device)


if __name__ == "__main__":

    devices = joincliUtils.open_local_devices()

    if devices is None:
        if arguments.apikey is None:
            logger.info("Apikey is not given, and no Environ value detected.")
            logger.info("Use -ak to set your apikey!")
            sys.exit(1)
        else:
            setup_devices(devices)
    elif arguments.update:
        update_devices(devices)
    elif arguments.register:
        register_new_device(devices)
    else:
        logger.info("No arguments!")
