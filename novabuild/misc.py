# -*- coding: utf-8 -*- ex:set ts=4 et:

from exceptions import Exception

def check_code(code, module):
    if code != 0:
        raise Exception("Could not fetch module %s" % module.name)
