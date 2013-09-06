#!/usr/bin/env python
# -*- coding: utf-8 -*- ex:set sw=4 ts=4 et:

import commands
from chroot import Chroot
from modules import ModuleSet

import ConfigParser
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
    return ModuleSet(os.path.join('modulesets', name))


def get_argument_parser(config):
    parser = argparse.ArgumentParser(prog="novabuild", description="Build Debian packages",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-c', '--chroot', dest='chroot', type=Chroot,
                        help="chroot installation to use")
    parser.add_argument('-m', '--moduleset', dest='moduleset', type=create_moduleset,
                        help="moduleset to use")
    parser.add_argument('-a', '--arch', dest='arch', type=str, default=None,
                        help="architecture")

    if config.has_section('environment'):
        parser.set_defaults(**dict(config.items('environment')))

    subparsers = parser.add_subparsers(help='sub-command')

    for cmd in dir(commands):
        if not cmd.startswith('_'):
            cmdmod = getattr(commands, cmd)
            subparser = subparsers.add_parser(cmd)
            cmdmod.register_arguments(subparser)
            if config.has_section(cmd):
                subparser.set_defaults(**dict(config.items(cmd)))
            subparser.set_defaults(func=cmdmod.main)

    return parser


def main(args):
    ensure_data_dir()

    config = ConfigParser.RawConfigParser()
    if os.path.exists('novabuild.cfg'):
        config.read('novabuild.cfg')

    parser = get_argument_parser(config)
    args = parser.parse_args(args[1:])

    # The default architecture will always be the current one.
    if args.arch is None:
        args.arch = os.popen('dpkg --print-architecture').readline().strip()

    try:
        status = args.func(args)
    except:
        traceback.print_exc()
        status = -1

    if args.chroot is not None:
        args.chroot.end_session()

    return status
