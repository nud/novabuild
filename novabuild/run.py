# -*- coding: utf-8 -*- ex:set ts=4 et:

import os

def system(cmd):
    from colours import brown
    print brown(cmd)
    return os.system(cmd)

def run(cmd, input = None):
    from subprocess import Popen, PIPE
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    if input is not None:
        stdin.write(input)
    output = p.communicate()
    if p.returncode != 0:
        raise Exception('Command "%s" exited with non-zero status (%d)' % (cmd, p.returncode))
    return output
