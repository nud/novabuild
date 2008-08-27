# -*- coding: utf-8 -*- ex:set ts=4 et:

import os
from novabuild.debcontrol import PackageControlParser
from novabuild.changelog import *
from novabuild.run import system
from novabuild.colours import blue
from novabuild.misc import check_code

import kernelmodule


class BuildMethod(kernelmodule.BuildMethod):
    def get_wrapper_script(self):
        lvers = self.moduleset['linux']['Version']
        lpath = self.chroot.abspath('~/tmp-build-dir/linux-%s' % lvers)

        zvers = self.moduleset['zaptel']['Version']
        zpath = self.chroot.abspath('~/tmp-build-dir/zaptel-%s' % zvers)

        return ''.join(["export KVERS=%s\n" % lvers,
                        "export KVER=%s\n" % lvers,
                        "export LINUX=%s\n" % lpath,
                        "export ZAPDIR=%s\n" % zpath,
                        "export USE_SANGOMA=1\n",
                        "./patches/clean_old_wanpipe.sh patches/kdrivers/include $LINUX/include/linux\n",
                        "exec fakeroot dpkg-buildpackage\n"])

    def setup_build_env(self, debian_dir, build_dir, module):
        kernelmodule.BuildMethod.setup_build_env(self, debian_dir, build_dir, module)

        path = self.chroot.abspath('~/tmp-build-dir/', internal=False)

        # Uncompress the zaptel tarball
        print blue('Uncompressing linux tarball')
        linux = self.moduleset['linux']
        filename = os.path.join('tarballs', linux['Basename'])
        linpath = self.chroot.abspath('~/tmp-build-dir/linux-%s' % linux['Version'], internal=False)
        check_code(system('tar xzf %s -C %s' % (filename, path)), module)
        check_code(system('cp autobuild/debian/config-%s-i386 %s/.config' % (linux['Version'], linpath)), module)
        check_code(self.chroot.system('make dep modules', cwd=self.chroot.abspath('~/tmp-build-dir/linux-%s' % linux['Version'])), module)

        # Uncompress the zaptel tarball
        print blue('Uncompressing zaptel tarball')
        filename = os.path.join('tarballs', self.moduleset['zaptel']['Basename'])
        check_code(system('tar xzf %s -C %s' % (filename, path)), module)
