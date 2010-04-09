# -*- coding: utf-8 -*- ex:set ts=4 et:

from novabuild.commands.build import build
from novabuild.colours import red, blue
import sys

def main(chroot, moduleset, args):
    for module in moduleset:
        try:
            print blue("Building '%s'" % moduleset[module].name)
            build(chroot, moduleset, moduleset[module], recursive=True)
        except Exception, e:
            print red("Exception %s: %s" % (e.__class__.__name__, e))
            return 1
    return 0
