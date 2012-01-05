# -*- coding: utf-8 -*- ex:set ts=4 et:

from novabuild.commands.build import build
from novabuild.colours import red, blue
import sys


def register_arguments(parser):
    parser.description = 'build all the packages'


def main(args):
    for mod_name in args.moduleset:
        try:
            module = args.moduleset[mod_name]
            print blue("Building '%s'" % module.name)
            build(args.chroot, args.moduleset, module, recursive=True)
        except Exception, e:
            print red("Exception %s: %s" % (e.__class__.__name__, e))
            return 1
    return 0
