# -*- coding: utf-8 -*- ex:set sw=4 ts=4 et:

import os
import run
import env

class Chroot(object):
    def __init__(self, name):
        self.user = env.get_user_name()
        self.name = name
        self.session = None

        self.root_dir = '/chroots/%s-%s' % (self.user, self.name)

    def abspath(self, path, cwd=None, root=False, internal=True):
        homedir = root and '/root' or '/home/%s' % self.user

        if path.startswith('~/'):
            path = os.path.join(homedir, path[2:])
        elif not path.startswith('/'):
            if cwd is None: cwd = homedir
            path = os.path.join(cwd, path)

        # Lately schroot has been mounting the real home directory into the chroot,
        # so we need to return the real homedir in any case.
        if not internal and not path.startswith(homedir):
            path = os.path.join(self.root_dir, path[1:])

        return path

    def get_home_dir(self, root=False):
        if root:
            return os.path.join(self.root_dir, 'root')
        else:
            return '/home/%s' % self.user

    def start_session(self):
        if self.session is None:
            cmd = 'schroot -b -c %s-%s' % (self.user, self.name)
            self.session = run.run(cmd)[-1].strip()

    def end_session(self):
        if self.session is not None:
            run.system('schroot -e -c %s' % self.session)
            self.session = None

    def system(self, cmd, cwd=None, root=False):
        if root:
            user = 'root'
            if cwd is None: cwd = '/root'
        else:
            user = self.user
            if cwd is None: cwd = '/home/%s' % user

        if self.session is not None:
            opts = '-r -c %s' % self.session
        else:
            opts = '-c %s-%s' % (self.user, self.name)

        cmd = 'schroot -u %s %s -d %s -- %s' % (user, opts, cwd, cmd)
        return run.system(cmd)
