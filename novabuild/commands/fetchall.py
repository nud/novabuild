# -*- coding: utf-8 -*- ex:set ts=4 et:

from novabuild.commands.fetch import fetch
from novabuild.colours import red, blue
import sys

def main(moduleset, args):
    status = 0

    for module in sorted(moduleset):
        try:
            print blue("Fetching '%s' from '%s'" % (moduleset[module].name, moduleset[module]['Source']))
            fetch(moduleset[module])
        except Exception, e:
            print red(e)
            status = 1

    sys.exit(status)
