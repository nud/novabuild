# -*- coding: utf-8 -*- ex:set ts=4 et:

from novabuild.run import system
from novabuild.colours import blue
from novabuild.misc import check_code


def build_module(module, chroot, moduleset, build_dir):
   print blue("Building '%s' '%s'" % (module.name, module['Version']))
   code = system('cp autobuild/debian/config-%s-i386 %s/.config' % (module['Version'], build_dir))
   check_code(code, module)

   code = chroot.system('make-kpkg --revision=novacom.i386.3.0 kernel_image kernel_headers kernel_source',
                         cwd=chroot.abspath('~/tmp-build-dir/linux-%s' % module['Version']), root=True)
   check_code(code, module)
