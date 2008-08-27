# -*- coding: utf-8 -*- ex:set ts=4 et:

import base

from novabuild.run import system
from novabuild.colours import blue
from novabuild.misc import check_code


class BuildMethod(base.BuildMethod):
    def build_module(self, module, build_dir):
        print blue("Building '%s' '%s'" % (module.name, module['Version']))
        code = system('cp autobuild/debian/config-%s-i386 %s/.config' % (module['Version'], build_dir))
        check_code(code, module)

        cwd = self.chroot.abspath('~/tmp-build-dir/linux-%s' % module['Version'])
        code = self.chroot.system('make-kpkg --revision=novacom.i386.3.0 kernel_image kernel_headers kernel_source',
                                  cwd=cwd, root=True)
        check_code(code, module)
