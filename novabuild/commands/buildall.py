# -*- coding: utf-8 -*- ex:set ts=4 et:

from novabuild.config import ModuleSetParser
from novabuild.commands.build import build
from novabuild.colours import red, blue
import sys

def main(chroot, moduleset, args):
    status = 0

    for package in sorted(moduleset.sections()):
        try:
            print blue("Building '%s'" % package)
            build(chroot, moduleset, package)
        except Exception, e:
            print red(e)
            status = 1

    sys.exit(status)
