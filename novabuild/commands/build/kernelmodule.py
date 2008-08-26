# -*- coding: utf-8 -*- ex:set ts=4 et:

import os
from novabuild.debcontrol import PackageControlParser
from novabuild.changelog import *
from novabuild.run import system
from novabuild.colours import blue
from novabuild.misc import check_code

from classic import install_dependencies, update_changelog


wrapper_script = '~/tmp-build-dir/build-wrapper.sh'


def save_wrapper_script(chroot, moduleset):
    fp = file(chroot.abspath(wrapper_script, internal=False), 'w')

    fp.write("export KVERS=%s\n" % moduleset['linux']['Version'])
    fp.write("export USE_SANGOMA=1\n")
    fp.write("exec fakeroot dpkg-buildpackage\n");


def build_module(module, chroot, moduleset, BUILD_DIR):
    DEBIAN_DIR = os.path.join('autobuild', 'debian', 'debian-%s' % module.name)

    code = system('cp -r %s %s/debian' % (DEBIAN_DIR, BUILD_DIR))
    check_code(code, module)

    install_dependencies(module, chroot, BUILD_DIR)

    update_changelog(module, BUILD_DIR, DEBIAN_DIR)

    print blue("Writing the wrapper script for module building")
    save_wrapper_script(chroot, moduleset)

    print blue("Building '%s' '%s'" % (module.name, module['Version']))
    code = chroot.system('sh ' + chroot.abspath(wrapper_script),
                         cwd=chroot.abspath('~/tmp-build-dir/%s-%s' % (module.name, module['Version'])))
    check_code(code, module)
