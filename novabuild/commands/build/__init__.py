# -*- coding: utf-8 -*- ex:set ts=4 et:

import os, sys, glob
from novabuild.run import system
from novabuild.colours import red, blue
from novabuild.misc import check_code
from exceptions import Exception


def build_module(module, chroot, moduleset, build_dir):
    print blue("Using build method '%s'" % module['Build-Method'])

    pymodule = __import__("novabuild.commands.build.%s" % module['Build-Method'],
                          globals(), locals(), ["BuildMethod"])
    method = pymodule.BuildMethod(chroot, moduleset)
    method.build_module(module, build_dir)


def build(chroot, moduleset, module):
    BUILD_DIR = os.path.join(chroot.get_home_dir(), 'tmp-build-dir',
                             '%s-%s' % (module.name, module['Version']))

    code = chroot.system('rm -rf /home/%s/tmp-build-dir' % chroot.user, root=True)
    check_code(code, module)

    code = system('mkdir -p %s' % os.path.dirname(BUILD_DIR))
    check_code(code, module)

    build_module(module, chroot, moduleset, BUILD_DIR)

    if module['Install']:
        packages_to_install = [i.strip() for i in module['Install'].split(',')]
        if packages_to_install != []:
            print blue("Installing packages '%s'" % "', '".join(packages_to_install))
            packages = [os.path.basename(i) for i in glob.glob(chroot.abspath('~/tmp-build-dir/*.deb', internal=False))]
            packages = [chroot.abspath('~/tmp-build-dir/%s' % package) for package in packages
                                                     if package.split('_', 1)[0] in packages_to_install]
            code = chroot.system("dpkg -i %s" % ' '.join(packages), root=True)
            check_code(code, module)

    code = system('mv -f %s/*.deb repository/' % os.path.dirname(BUILD_DIR))


def main(chroot, moduleset, args):
    module = moduleset[args[0]]

    try:
        build(chroot, moduleset, module)

    except Exception, e:
        print red(e)
        sys.exit(1)
