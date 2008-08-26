# -*- coding: utf-8 -*- ex:set ts=4 et:

import os, sys, glob
from novabuild.debcontrol import PackageControlParser
from novabuild.changelog import *
from novabuild.run import system
from novabuild.colours import red, blue
from novabuild.misc import check_code
from exceptions import Exception


def uncompress_tarball(module, destination):
    filename = os.path.join('tarballs', module['Basename'])
    if not os.path.exists(filename):
        raise Exception("You must fetch the package '%s' before building it." % module.name)

    dest_parent = os.path.dirname(destination)

    print blue("Uncompressing '%s'" % filename)
    if filename.endswith('.tar.bz2') or filename.endswith('.tbz'):
        check_code(system('tar xjf %s -C %s' % (filename, dest_parent)), module)
    elif filename.endswith('.tar.gz') or filename.endswith('.tgz'):
        check_code(system('tar xzf %s -C %s' % (filename, dest_parent)), module)
    elif filename.endswith('.zip'):
        check_code(system('unzip %s -d %s' % (filename, dest_parent)), module)
    else:
        raise Exception("Cannot find the type of the archive.")

    # Put the directory in the tarball in the right directory
    code = system('mv %s/* %s' % (dest_parent, destination))
    #check_code(code, module)  FIXME: we don't want to fail when "cannot move to itself"


def build_module(module, chroot, build_dir):
    print blue("Using build method '%s'" % module['Build-Method'])

    pymodule = __import__("novabuild.commands.build.%s" % module['Build-Method'],
                          globals(), locals(), ["build_module"])
    pymodule.build_module(module, chroot, build_dir)


def build(chroot, module):
    BUILD_DIR = os.path.join(chroot.get_home_dir(), 'tmp-build-dir',
                             '%s-%s' % (module.name, module['Version']))

    code = chroot.system('rm -rf /home/%s/tmp-build-dir' % chroot.user, root=True)
    check_code(code, module)

    code = system('mkdir -p %s' % os.path.dirname(BUILD_DIR))
    check_code(code, module)

    uncompress_tarball(module, BUILD_DIR)
    build_module(module, chroot, BUILD_DIR)

    packages_to_install = [i.strip() for i in module['Install'].split(',')]
    if packages_to_install != []:
        print blue("Installing packages '%s'" % "', '".join(packages_to_install))
        packages = [os.path.basename(i) for i in glob.glob(chroot.abspath('~/tmp-build-dir/*.deb', internal=False))]
        for package in packages:
            if package.split('_',1)[0] in packages_to_install:
                code = chroot.system("dpkg -i %s" % chroot.abspath('~/tmp-build-dir/%s' % package), root=True)
                check_code(code, module)

    code = system('mv -f %s/*.deb repository/' % os.path.dirname(BUILD_DIR))


def main(chroot, moduleset, args):
    module = moduleset[args[0]]

    try:
        build(chroot, module)

    except Exception, e:
        print red(e)
        sys.exit(1)
