# -*- coding: utf-8 -*- ex:set ts=4 et:

from novabuild.config import ModuleSetParser
from novabuild.commands.fetch import fetch
from novabuild.colours import red, blue
import sys

def main(argv):
    moduleset = argv[0]
    c = ModuleSetParser(moduleset)

    status = 0

    for package in sorted(c.sections()):
        try:
            print blue("Fetching '%s' from '%s'" % (package, c.get(package, 'source')))
            fetch(c, package)
        except Exception, e:
            print red(e)
            status = 1

    sys.exit(status)
