#!/usr/bin/env python
# -*- coding: utf-8 -*- ex:set ts=4 et:

import novabuild.commands as commands
import sys
import os

sys.path.insert(0, os.path.abspath('.'))

def usage():
    print 'Usage: ' + sys.argv[0] + ' [command] [options]'
    print
    print 'available commands:'
    print '  prepare        prepare a new build environment'
    print '  list           list the available packages'
    print '  fetch          fetch the requested package'
    print '  fetchall       fetch all the packages'
    print
    print 'Use ' + sys.argv[0] + ' [command] --help for more information.'

if len(sys.argv) < 2:
    usage()
    sys.exit(2)

if sys.argv[1] in ('-h', '--help'):
    usage()
    sys.exit(0)

# Arguments to pass to the commands
argv = sys.argv[2:]

if sys.argv[1] == 'prepare':
    commands.prepare.main(argv)

if sys.argv[1] == 'list':
    commands.pkglist.main(argv)

if sys.argv[1] == 'fetch':
    commands.fetch.main(argv)

if sys.argv[1] == 'fetchall':
    commands.fetchall.main(argv)
