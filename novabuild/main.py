#!/usr/bin/env python
# -*- coding: utf-8 -*- ex:set sw=4 ts=4 et:

import commands
from chroot import Chroot
from modules import ModuleSet

import os
import getopt
import traceback


class NovabuildError(Exception):
    pass


def usage(binname):
    print 'Usage: %s [command] [options]' % binname
    print
    print 'available commands:'
    print '  shell          open a shell'
    print '  prepare        prepare a new build environment'
    print '  list           list the available packages'
    print '  fetch          fetch the requested package'
    print '  fetchall       fetch all the packages'
    print '  build          build a single package'
    print '  buildall       build all the packages'
    print
    print 'Use %s [command] --help for more information.' % binname


def ensure_data_dir():
    cwd = os.getcwd()
    while True:
        if os.path.exists(os.path.join(cwd, 'modulesets')):
            os.chdir(cwd)
            return
        cwd = os.path.dirname(cwd)
        if cwd == '/':
            raise NovabuildError('Not a novabuild repository (or any of the parent directories)')


def main(args):
    binname = args.pop(0)

    try:
        opts, args = getopt.getopt(args, 'hc:m:', ['help', 'chroot=', 'moduleset='])
    except getopt.GetoptError, e:
        # print help information and exit:
        print str(e) # will print something like "option -a not recognized"
        usage(binname)
        return 2

    chroot_name = None
    moduleset_name = None

    for o, a in opts:
        if o in ('-h', '--help'):
            usage(binname)
            return 0
        elif o in ('-c', '--chroot'):
            chroot_name = a
        elif o in ('-m', '--moduleset'):
            moduleset_name = a

    # At least one remaining argument to specify the command.
    if len(args) < 2:
        usage(binname)
        return 2

    ensure_data_dir()

    # Arguments to pass to the commands
    chroot = None
    if chroot_name:
        chroot = Chroot(chroot_name)

    moduleset = None
    if moduleset_name:
        filename = os.path.join('modulesets', moduleset_name)
        moduleset = ModuleSet(filename)

    command = args[1]
    cmdargs = args[2:]
    status = -1

    try:
        if command == 'shell':
            status = commands.shell.main(chroot, cmdargs)

        elif command == 'prepare':
            status = commands.prepare.main(chroot, cmdargs)

        elif command == 'list':
            status = commands.pkglist.main(chroot, moduleset, cmdargs)

        elif command == 'fetch':
            status = commands.fetch.main(moduleset, cmdargs)

        elif command == 'fetchall':
            status = commands.fetchall.main(moduleset, cmdargs)

        elif command == 'build':
            chroot.start_session()
            status = commands.build.main(chroot, moduleset, cmdargs)

        elif command == 'buildall':
            chroot.start_session()
            status = commands.buildall.main(chroot, moduleset, cmdargs)

        elif command == 'installpackages':
            chroot.start_session()
            status = commands.installpackages.main(chroot, moduleset, cmdargs)

        else:
            print "Unknown command: %s" % command
            usage(binname)
            status = 2
    except:
        traceback.print_exc()
        status = -1

    if chroot is not None:
        chroot.end_session()

    return status
