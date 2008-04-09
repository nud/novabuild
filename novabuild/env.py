# -*- coding: utf-8 -*- ex:set ts=4 et:

import os

def get_user_name():
    return os.getenv('SUDO_USER') or os.getenv('USER')

def get_uid():
    return int(os.getenv('SUDO_UID') or os.getenv('UID'))
