# -*- coding: utf-8 -*- ex:set ts=4 et:

import os
import sys
import subprocess
from exceptions import Exception

from colours import brown

def system(cmd, root=False, cwd=None): # FIXME
    env =  os.environ.copy()

    if root:
        cmd = 'sudo ' + cmd

    if cwd:
        cmd = "cd %s; %s" % (cwd, cmd)

    print brown(cmd)
    return subprocess.call(cmd, shell=True, env=env)

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
