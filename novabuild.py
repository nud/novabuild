#!/usr/bin/env python
# -*- coding: utf-8 -*- ex:set sw=4 ts=4 et:

import novabuild.commands as commands
from novabuild.chroot import Chroot
from novabuild.modules import ModuleSet
import sys
import os
import getopt

sys.path.insert(0, os.path.abspath('.'))

def usage():
    print 'Usage: ' + sys.argv[0] + ' [command] [options]'
    print
    print 'available commands:'
    print '  prepare        prepare a new build environment'
    print '  list           list the available packages'
    print '  fetch          fetch the requested package'
    print '  fetchall       fetch all the packages'
    print '  build          build a single package'
    print
    print 'Use ' + sys.argv[0] + ' [command] --help for more information.'

try:
    opts, args = getopt.getopt(sys.argv[1:], 'hc:m:',
                               ['help', 'chroot=', 'moduleset='])
except getopt.GetoptError, e:
    # print help information and exit:
    print str(e) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

chroot_name = None
moduleset_name = None

for o, a in opts:
    if o in ('-h', '--help'):
        usage()
        sys.exit(0)
    elif o in ('-c', '--chroot'):
        chroot_name = a
    elif o in ('-m', '--moduleset'):
        moduleset_name = a

# At least one remaining argument to specify the command.
if len(args) < 1:
    usage()
    sys.exit(2)

# Arguments to pass to the commands
chroot = chroot_name and Chroot(chroot_name) or None
moduleset = moduleset_name and ModuleSet(moduleset_name) or None
command = args[0]
args = args[1:]

print opts
print args

if command == 'shell':
    commands.shell.main(chroot, args)

if command == 'prepare':
    commands.prepare.main(chroot, args)

if command == 'list':
    commands.pkglist.main(moduleset, args)

if command == 'fetch':
    commands.fetch.main(moduleset, args)

if command == 'fetchall':
    commands.fetchall.main(moduleset, args)

if command == 'build':
    commands.build.main(chroot, moduleset, args)

if command == 'buildall':
    commands.buildall.main(chroot, moduleset, args)

if command == 'installpackages':
    commands.installpackages.main(chroot, moduleset, args)
