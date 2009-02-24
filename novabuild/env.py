# -*- coding: utf-8 -*- ex:set ts=4 et:

import os

def get_user_name():
    try:
        return os.getenv('SUDO_USER') or os.getenv('USER')
    except TypeError:
        return None

def get_uid():
    try:
        return int(os.getenv('SUDO_UID') or os.getenv('UID'))
    except TypeError:
        return None
