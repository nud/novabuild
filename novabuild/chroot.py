# -*- coding: utf-8 -*- ex:set sw=4 ts=4 et:

import os
import run
import env

class Chroot(object):
    def __init__(self, name):
        self.user = env.get_user_name()
        self.name = name

        self.root_dir = '/chroots/%s-%s' % (self.user, self.name)

    def abspath(self, path, cwd=None, root=False, internal=True):
        homedir = root and '/root' or '/home/%s' % self.user

        if path.startswith('~/'):
            path = os.path.join(homedir, path[2:])
        elif not path.startswith('/'):
            if cwd is None: cwd = homedir
            path = os.path.join(cwd, path)

        if internal:
            path = os.path.join(self.root_dir, path)

        return path

    def get_home_dir(self, root=False):
        if root:
            homedir = 'root'
        else:
            homedir = 'home/%s' % self.user

        return os.path.join(self.root_dir, homedir)

    def system(self, cmd, cwd=None, root=False):
        if root:
            user = 'root'
            if cwd is None: cwd = '/root'
        else:
            user = self.user
            if cwd is None: cwd = '/home/%s' % user

        cmd = 'schroot -u %s -c %s-%s -d %s -- %s' % (user, self.user, self.name, cwd, cmd)
        return run.system(cmd)
