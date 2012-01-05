# -*- coding: utf-8 -*- ex:set ts=4 et:

from novabuild.commands.fetch import fetch
from novabuild.colours import red, blue
import sys

def register_arguments(parser):
    parser.description = 'Fetch all the tarballs'

def main(args):
    for mod_name in sorted(args.moduleset):
        try:
            module = args.moduleset[mod_name]
            print blue("Fetching '%s' from '%s'" % (module.name, module['Source']))
            fetch(module)
        except Exception, e:
            print red(e)
            status = 1

    return 0
