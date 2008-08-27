# -*- coding: utf-8 -*- ex:set ts=4 et:

import os
from novabuild.debcontrol import PackageControlParser
from novabuild.changelog import *
from novabuild.run import system
from novabuild.colours import blue
from novabuild.misc import check_code

import classic


class BuildMethod(classic.BuildMethod):
    wrapper_script = '~/tmp-build-dir/build-wrapper.sh'

    def get_wrapper_script(self):
        return ''.join(["export KVERS=%s\n" % self.moduleset['linux']['Version'],
                        "export LINUX=/usr/src/linux-headers-$KVERS\n",
                        "export USE_SANGOMA=1\n",
                        "exec fakeroot dpkg-buildpackage\n"])

    def save_wrapper_script(self):
        path = self.chroot.abspath(self.wrapper_script, internal=False)
        file(path, 'w').write(self.get_wrapper_script())

    def setup_build_env(self, *args):
        classic.BuildMethod.setup_build_env(self, *args)
        self.save_wrapper_script()

    def build(self, module):
        cmd = 'sh ' + self.chroot.abspath(self.wrapper_script)
        cwd = self.chroot.abspath('~/tmp-build-dir/%s-%s' % (module.name, module['Version']))
        code = self.chroot.system(cmd, cwd=cwd)
        check_code(code, module)
