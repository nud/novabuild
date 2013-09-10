# -*- coding: utf-8 -*- ex:set ts=4 et:

from novabuild.chroot import Chroot
import sys


def register_arguments(parser, config):
    parser.description = 'Spawn a shell in the chroot'
    parser.add_argument('-r', '--root', dest='root', action='store_true', help='root shell')

    if config.has_section('shell'):
        parser.set_defaults(**dict(config.items('shell')))


def main(args):
    return args.chroot.system('', root=args.root)
