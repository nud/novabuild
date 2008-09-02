# -*- coding: utf-8 -*- ex:set ts=4 et:

import base

from novabuild.run import system
from novabuild.colours import blue
from novabuild.misc import check_code


class BuildMethod(base.BuildMethod):
    REV_TAG="novacom.i386.3.0"

    # Set up the dpkg environment for the build.
    def setup_build_env(self, module, build_dir):
        self.uncompress_tarball(module, build_dir)

        print blue("Configuring the kernel")
        code = system('cp autobuild/debian/config-%s-i386 %s/.config' % (module['Version'], build_dir))
        check_code(code, module)


    def build_module(self, module, build_dir):
        self.setup_build_env(module, build_dir)

        print blue("Building linux kernel '%s'" % module['Version'])
        cwd = self.chroot.abspath('~/tmp-build-dir/linux-%s' % module['Version'])
        code = self.chroot.system('make-kpkg --revision=%s kernel_image kernel_headers kernel_source' % self.REV_TAG,
                                  cwd=cwd, root=True)
        check_code(code, module)


    def list_module_packages(self, module):
        version = module['Version']
        return ["linux-%s-%s_%s_i386.deb" % (p, version, self.REV_TAG) for m in ('headers', 'image', 'source')]
