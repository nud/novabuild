# -*- coding: utf-8 -*- ex:set ts=4 et:

import os
import sys
from exceptions import Exception

from colours import brown

def system(cmd):
    print brown(cmd)
    return os.system(cmd)

def run(cmd, input = None):
    from subprocess import Popen, PIPE
    print brown(cmd)
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=sys.stderr)
    if input is not None:
        stdin.write(input)

    lines = []
    for line in p.stdout:
        lines.append(line)
        print line,

    p.wait()
    if p.returncode != 0:
        raise Exception('Command "%s" exited with non-zero status (%d)' % (cmd, p.returncode))
    return lines

def check_code(code, module):
    if code != 0:
        raise Exception("Could not handle module %s" % module.name)
