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
        if 'linux' in self.moduleset:
            kvers = self.moduleset['linux']['Version']
        else:
            # FIXME: How god, this is ugly!
            kvers = '$(/bin/ls /usr/src/ | grep -E "linux-headers-2\.6.*686-bigmem" | grep -o "2\.6.*686-bigmem")'

        return ''.join(["export KVERS=%s\n" % kvers,
                        "export LINUX=/usr/src/linux-headers-$KVERS\n",
                        "export KSRC=$LINUX\n",
                        "export USE_SANGOMA=1\n",
                        "exec dpkg-buildpackage -rfakeroot -b -uc\n"])

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
