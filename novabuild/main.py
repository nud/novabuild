#!/usr/bin/env python
# -*- coding: utf-8 -*- ex:set sw=4 ts=4 et:

import commands
from chroot import Chroot
from modules import ModuleSet

import os
import argparse
import traceback


class NovabuildError(Exception):
    pass


def ensure_data_dir():
    cwd = os.getcwd()
    while True:
        if os.path.exists(os.path.join(cwd, 'modulesets')):
            os.chdir(cwd)
            return
        cwd = os.path.dirname(cwd)
        if cwd == '/':
            raise NovabuildError('Not a novabuild repository (or any of the parent directories)')


def create_moduleset(name):
    ensure_data_dir()
    return ModuleSet(os.path.join('modulesets', name))


def get_argument_parser():
    parser = argparse.ArgumentParser(prog="novabuild", description="Build Debian packages",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-c', '--chroot', dest='chroot', required=True, type=Chroot,
                        help="chroot installation to use")
    parser.add_argument('-m', '--moduleset', dest='moduleset', required=True, type=create_moduleset,
                        help="moduleset to use")

    subparsers = parser.add_subparsers(help='sub-command')

    for cmd in dir(commands):
        if not cmd.startswith('_'):
            cmdmod = getattr(commands, cmd)
            subparser = subparsers.add_parser(cmd)
            cmdmod.register_arguments(subparser)
            subparser.set_defaults(func=cmdmod.main)

    return parser


def main(args):
    parser = get_argument_parser()
    args = parser.parse_args(args[1:])

    try:
        status = args.func(args)
    except:
        traceback.print_exc()
        status = -1

    if args.chroot is not None:
        args.chroot.end_session()

    return status
