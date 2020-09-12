import argparse
import json
import os
import re
from . import logger


# from . import logger

def api_regex(_string, pat=re.compile(r"\w{32}")):
    r"""
    Check if given string matches the API pattern.

    :param _string: api string
    :param pat: Pattern, Default matches re.compile(r"\w{32}")
    :return: String if check passes
    """
    if not pat.match(_string):
        raise argparse.ArgumentTypeError
    return _string


def str2bool(arg):
    """
    Converts unknonwn value to it's corresponding bool
    :param arg: str
    :return: bool
    """
    if arg.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    if arg.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected!')


def file_dialog():
    """
        Check and use Tkinter for file dialog, or call generate_default.

        ::returns:: filename
    """
    try:
        import tkinter
        from tkinter import filedialog

        options = {
                'defaultextension': '.ini',
                'filetypes':        [('json config files', '.json')],
                'initialdir':       os.environ['ROOT_DIR'],
                'initialfile':      'devices.json',
                'title':            'Select Project Configuration File'
                }
        root = tkinter.Tk()
        filename = filedialog.askopenfilename(**options)
        root.destroy()
        return filename
    except ImportError:
        logger.debug('tkinter not installed')
        return


def open_local_devices():
    """
    Attempt to open default device file, or open file fio
    :return: Devices json object
    """
    try:
        with open("devices.json") as deviceJSON:
            return json.loads(deviceJSON.read())
    except json.JSONDecodeError:
        deviceJSON = file_dialog()
    return json.loads(deviceJSON.read())


def decode_UTF8(data):
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    except Exception as e:
        raise (e)
