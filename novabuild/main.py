#!/usr/bin/env python
# -*- coding: utf-8 -*- ex:set sw=4 ts=4 et:

import commands
import env
from chroot import Chroot
from modules import ModuleSet

import argparse
import ConfigParser
import jinja2
import os
import re
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


def get_config_vars(config):
    v = {'distro': env.get_distro_codename()}
    if config.has_section('vars'):
        v.update(config.items('vars'))
    return v


def read_configuration(filenames):
    config = ConfigParser.RawConfigParser()

    for filename in filenames:
        filename = os.path.expanduser(filename)
        if os.path.exists(filename):
            config.read(filename)

    expr_vars = get_config_vars(config)

    for section in config.sections():
        items = config.items(section)

        m = re.match('^([a-z_-]+) if (.*)$', section)
        if m:
            if not eval(m.group(2), {'__builtins__': None}, expr_vars):
                continue
            config.remove_section(section)
            section = m.group(1)

            if not config.has_section(section):
                config.add_section(section)
        else:
            items = config.items(section)

        for name, value in items:
            new_value = re.sub('{([a-z_]+)}', lambda m: expr_vars[m.group(1)], value)
            config.set(section, name, new_value)

    return config



class ModuleSetFactory(object):
    def __init__(self, config):
        self._vars = get_config_vars(config)

    def __call__(self, name):
        class RelEnvironment(jinja2.Environment):
            """Override join_path() to enable relative template paths."""
            def join_path(self, template, parent):
                return os.path.join(os.path.dirname(parent), template)

        env = RelEnvironment(loader=jinja2.FileSystemLoader('modulesets'))
        template = env.get_template(name)

        moduleset = ModuleSet()
        moduleset.readfp(template.render(**self._vars).splitlines())
        return moduleset


def get_argument_parser(config):
    parser = argparse.ArgumentParser(prog="novabuild", description="Build Debian packages",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-c', '--chroot', dest='chroot', type=Chroot,
                        help="chroot installation to use")
    parser.add_argument('-m', '--moduleset', dest='moduleset', type=ModuleSetFactory(config),
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

    config = read_configuration(['~/.novabuildrc', 'novabuild.cfg'])

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
