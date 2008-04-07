# -*- coding: utf-8 -*- ex:set ts=4 et:

import os
import run

class Chroot(object):
    def __init__(self, name):
        if 'SUDO_USER' in os.environ:
            self.user = os.environ['SUDO_USER']
        else:
            self.user = os.environ['USER']

        self.name = name

        self.root_dir = '/chroots/%s-%s' % (self.user, self.name)

    def get_home_dir(self):
        return os.path.join(self.root_dir, 'root')

    def system(self, cmd, cwd = '/root'):
        cmd = 'schroot -c %s-%s -d %s %s' % (self.user, self.name, cwd, cmd)
        return run.system(cmd)
