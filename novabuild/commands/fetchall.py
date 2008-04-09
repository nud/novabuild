# -*- coding: utf-8 -*- ex:set ts=4 et:

from novabuild.config import ModuleSetParser
from novabuild.commands.fetch import fetch
from novabuild.colours import red, blue
import sys

def main(moduleset, args):
    status = 0

    for package in sorted(moduleset.sections()):
        try:
            print blue("Fetching '%s' from '%s'" % (package, moduleset.get(package, 'source')))
            fetch(moduleset, package)
        except Exception, e:
            print red(e)
            status = 1

    sys.exit(status)
