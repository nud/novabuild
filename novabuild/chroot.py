# -*- coding: utf-8 -*- ex:set sw=4 ts=4 et:

import os
import run
import env

class Chroot(object):
    def __init__(self, name):
        self.user = env.get_user_name()
        self.name = name

        self.root_dir = '/chroots/%s-%s' % (self.user, self.name)

    def get_home_dir(self):
        return os.path.join(self.root_dir, 'root')

    def system(self, cmd, cwd=None, root=False):
        if root:
            user = 'root'
            if cwd is None: cwd = '/root'
        else:
            user = self.user
            if cwd is None: cwd = '/home/%s' % user

        cmd = 'schroot -u %s -c %s-%s -d %s -- %s' % (user, self.user, self.name, cwd, cmd)
        return run.system(cmd)
