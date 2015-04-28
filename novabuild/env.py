# -*- coding: utf-8 -*- ex:set ts=4 et:

import os
import subprocess

def get_user_name():
    try:
        return os.getenv('SUDO_USER') or os.getenv('USER')
    except TypeError:
        return None

def get_home():
    return os.getenv('HOME')

def get_uid():
    try:
        return int(os.getenv('SUDO_UID') or os.getenv('UID'))
    except TypeError:
        return None

def get_distributor():
    return subprocess.check_output(['lsb_release', '-is']).strip()

def get_distro_codename():
    return subprocess.check_output(['lsb_release', '-cs']).strip()
